import shutil
import tempfile
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import json
import os
from datetime import datetime, timezone
import hmac, hashlib, time
import requests
import jwt
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization

app = FastAPI()

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
GITHUB_WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"].strip().strip('"').strip("'")
GITHUB_APP_ID = os.environ["GITHUB_APP_ID"].strip()

key_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
if key_path:
    GITHUB_APP_PRIVATE_KEY = (ROOT / key_path).read_text(encoding="utf-8")
else:
    # fallback if you store it inline with \n escapes
    GITHUB_APP_PRIVATE_KEY = os.environ["GITHUB_APP_PRIVATE_KEY"].replace("\\n", "\n")

assert GITHUB_APP_PRIVATE_KEY.startswith("-----BEGIN "), "PEM didn't start with BEGIN"
# Will raise if wrong/mangled:
serialization.load_pem_private_key(GITHUB_APP_PRIVATE_KEY.encode("utf-8"), password=None)

# ---------- UTILITY RELATED FUNCTIONS ----------
# For running shell commands
def run_cmd(cmd: list[str], cwd: str | None = None, check: bool = True,
            env: dict | None = None) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,              
            encoding="utf-8",       
            errors="replace",  
            env=env,
            check=check,
        )
        return (proc.returncode, proc.stdout, proc.stderr)
    except FileNotFoundError as e:
        raise RuntimeError(f"Command not found: {cmd[0]}") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n"
            f"exit={e.returncode}\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}"
        ) from e

# For parsing JSON safely, returns default if parsing fails
def _safe_json_loads(s: str, default):
    try: return json.loads(s)
    except Exception: return default

# For hiding parts of secret keys
def _mask(s: str | None, keep_start=4, keep_end=2):
    if not s: return s
    n = len(s)
    if n <= keep_start + keep_end: return "*" * n
    return s[:keep_start] + "*" * (n - keep_start - keep_end) + s[-keep_end:]

# Read a small code snippet (±ctx lines) from a file path relative to `root`.
# Returns None if file/line missing or unreadable.
def _read_snippet(root: str, rel_file: str | None, line: int | None, ctx=2):
    if not rel_file or not line: return None
    try:
        p = Path(root) / rel_file
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        line = int(line)
        s = max(1, line - ctx); e = min(len(lines), line + ctx)
        return {"start_line": s, "end_line": e, "code": "\n".join(lines[s-1:e])}
    except Exception:
        return None

# ---------- GIT APP INSTALLATION RELATED FUNCTIONS ----------
def verify_signature(body: bytes, sig_header: str, secret: str) -> bool:
    mac = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, sig_header or "")

def app_jwt(app_id: str, private_key_pem: str) -> str:
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 9 * 60, "iss": app_id}
    return jwt.encode(payload, private_key_pem, algorithm="RS256")

def installation_token(app_jwt_token: str, installation_id: int) -> str:
    r = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={"Authorization": f"Bearer {app_jwt_token}", "Accept": "application/vnd.github+json"},
    )
    r.raise_for_status()
    return r.json()["token"]

# ---------- AI RELATED FUNCTIONS ---------- 
# Build the LLM input payload with repo metadata, timestamp, and normalized findings.
def build_llm_payload(repo_url: str, branch: str, commit: str, temp_dir: str,
                      trivy_json: dict, gitleaks_json) -> dict:
    findings = []
    findings += _summarize_trivy(trivy_json, temp_dir)
    findings += _summarize_gitleaks(gitleaks_json, temp_dir)
    return {
        "repo": repo_url,
        "branch": branch,
        "commit": commit,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "findings": findings,
    }

# ---------- SCANNING TOOL FUNCTIONS ----------
# Convert Trivy's JSON output into a unified "findings" list covering:
# - secrets, vulnerabilities, and misconfigurations, plus small code snippets when possible.
def _summarize_trivy(trivy_json: dict, temp_dir: str):
    findings = []
    for res in (trivy_json.get("Results") or []):
        target = res.get("Target")
        # Secrets
        for sec in (res.get("Secrets") or []):
            findings.append({
                "tool": "trivy",
                "type": "secret",
                "rule_id": sec.get("RuleID"),
                "title": sec.get("Title") or sec.get("RuleID"),
                "severity": sec.get("Severity") or "UNKNOWN",
                "file": target,
                "start_line": sec.get("StartLine"),
                "end_line": sec.get("EndLine"),
                "match": _mask(sec.get("Match")),
                "snippet": _read_snippet(temp_dir, target, sec.get("StartLine")),
            })
        # Vulnerabilities
        for v in (res.get("Vulnerabilities") or []):
            findings.append({
                "tool": "trivy",
                "type": "vulnerability",
                "cve": v.get("VulnerabilityID"),
                "pkg": v.get("PkgName"),
                "installed": v.get("InstalledVersion"),
                "fixed": v.get("FixedVersion"),
                "severity": v.get("Severity"),
                "description": v.get("Description"),
                "primary_url": v.get("PrimaryURL"),
                "file": target,
            })
        # Misconfigurations
        for m in (res.get("Misconfigurations") or []):
            cm = m.get("CauseMetadata") or {}
            findings.append({
                "tool": "trivy",
                "type": "misconfiguration",
                "id": m.get("ID"),
                "title": m.get("Title"),
                "severity": m.get("Severity"),
                "description": m.get("Description"),
                "message": m.get("Message"),
                "resolution": m.get("Resolution"),
                "file": target,
                "start_line": (cm.get("StartLine") or cm.get("StartLineNumber")),
                "end_line": (cm.get("EndLine") or cm.get("EndLineNumber")),
                "snippet": _read_snippet(temp_dir, target, cm.get("StartLine") or cm.get("StartLineNumber")),
            })
    return findings

# Convert Gitleaks JSON (list or {"findings":[...]}) into unified "findings".
def _summarize_gitleaks(gitleaks_json, temp_dir: str):
    # gitleaks returns a list (or sometimes {"findings":[...]})
    items = gitleaks_json if isinstance(gitleaks_json, list) else (gitleaks_json.get("findings") or [])
    findings = []
    for f in items:
        findings.append({
            "tool": "gitleaks",
            "type": "secret",
            "rule_id": f.get("RuleID") or f.get("Rule"),
            "description": f.get("Description"),
            "file": f.get("File") or f.get("FilePath"),
            "start_line": f.get("StartLine"),
            "end_line": f.get("EndLine"),
            "secret": _mask(f.get("Secret") or f.get("Match")),
            "entropy": f.get("Entropy"),
            "tags": f.get("Tags"),
            "snippet": _read_snippet(temp_dir, f.get("File") or f.get("FilePath"), f.get("StartLine")),
        })
    return findings

# Clone a repo (branch or single commit), run Trivy & Gitleaks, normalize results,
# and return a summary + raw tool outputs for debugging.
def scan_repo_impl(repo_url: str, branch: str = "main", commit: str | None = None) -> dict:
    temp_dir = tempfile.mkdtemp(prefix="scan-")
    try:
        # Clone
        if commit:
            run_cmd(["git", "clone", "--no-checkout", repo_url, temp_dir])
            run_cmd(["git", "fetch", "--depth", "1", "origin", commit], cwd=temp_dir)
            run_cmd(["git", "checkout", commit], cwd=temp_dir)
        else:
            run_cmd(["git", "clone", "--depth", "1", "--branch", branch, repo_url, temp_dir])

        # Run tools
        trivy_rc, trivy_out, trivy_err = run_cmd(
            ["trivy", "fs", "--no-progress", "--format", "json",
             "--scanners", "vuln,secret,misconfig", temp_dir],
            check=False
        )
        gitleaks_rc, gitleaks_out, gitleaks_err = run_cmd(
            ["gitleaks", "detect", "--source", temp_dir,
             "--report-format", "json", "--no-banner"],
            check=False
        )

        # Parsing
        trivy_json = _safe_json_loads(trivy_out or "{}", {})
        gitleaks_json = _safe_json_loads(gitleaks_out or "[]", [])

        llm_input = build_llm_payload(repo_url, branch, commit, temp_dir, trivy_json, gitleaks_json)

        # ----- THIS IS FOR ME TO SEE RESULTS -----
        trivy_summary = _summarize_trivy(trivy_json, temp_dir) if trivy_rc == 0 else None
        gitleaks_summary = _summarize_gitleaks(gitleaks_json, temp_dir) if gitleaks_rc == 0 else None
        
        summary_payload = {
            "repo": repo_url,
            "branch": branch,
            "commit": commit,
            "summary": {
                "trivy": trivy_summary,
                "gitleaks": gitleaks_summary,
            },
        }
        print("SCAN COMPLETE:", json.dumps(summary_payload, indent=2))
        # -----------------------------------------

        # Build a clean response
        return {
            "status": "scanned",
            "repo": repo_url,
            "branch": branch,
            "commit": commit,
            "summary": {
                "trivy": _summarize_trivy(trivy_json, temp_dir) and {
                    "counts": {
                        "targets_scanned": len(trivy_json.get("Results") or []),
                        "vulnerabilities": sum(len(r.get("Vulnerabilities") or []) for r in (trivy_json.get("Results") or [])),
                        "misconfigurations": sum(len(r.get("Misconfigurations") or []) for r in (trivy_json.get("Results") or [])),
                        "secrets": sum(len(r.get("Secrets") or []) for r in (trivy_json.get("Results") or [])),
                    }
                },
                "gitleaks": {"leaks": len(llm_input["findings"]) - sum(len(r.get("Vulnerabilities") or []) + len(r.get("Misconfigurations") or []) + len(r.get("Secrets") or []) for r in (trivy_json.get("Results") or []))}
            },
            # CHANGE THIS TO LLM OUTPUT, USE THE INPUT WITHIN SCAN
            "llm_input": llm_input,
            "trivy": {"returncode": trivy_rc, "stderr": trivy_err, "json": trivy_json},
            "gitleaks": {"returncode": gitleaks_rc, "stderr": gitleaks_err, "json": gitleaks_json},
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/scan")
async def scan_handler(payload: dict):
    try:
        data = scan_repo_impl(
            repo_url=payload["repo_url"],
            branch=payload.get("branch", "main"),
            commit=payload.get("commit"),
        )
        return data
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/webhook/github")
async def handle_github_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(body, sig, GITHUB_WEBHOOK_SECRET):
        return JSONResponse(status_code=401, content={"error": "bad signature"})

    event = request.headers.get("X-GitHub-Event", "")
    if event == "ping":
        return {"ok": True, "pong": True}
    if event not in ("push", "pull_request"):
        return {"ignored": True, "event": event}

    payload = json.loads(body)
    owner = payload["repository"]["owner"]["login"]
    repo  = payload["repository"]["name"]

    if event == "push":
        branch = payload["ref"].split("/")[-1]
        commit = payload["after"]
    else:
        branch = payload["pull_request"]["head"]["ref"]
        commit = payload["pull_request"]["head"]["sha"]

    inst_id = payload["installation"]["id"]
    token = installation_token(app_jwt(GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY), inst_id)

    # Use short-lived installation token to clone
    repo_url = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"

    print(f"[webhook] {owner}/{repo}@{branch} {commit[:7]} (inst {inst_id})")
    background_tasks.add_task(scan_repo_impl, repo_url, branch, commit)
    return {"status": "accepted", "owner": owner, "repo": repo, "branch": branch, "commit": commit}
