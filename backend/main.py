import shutil
import tempfile
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import json

app = FastAPI()

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
    
def _safe_json_loads(s: str, default):
    try:
        return json.loads(s)
    except Exception:
        return default
    
def _summarize_trivy(data: dict) -> dict:
    # Trivy FS JSON typically has a top-level "Results": [...]
    vulns = secrets = misconfigs = targets = 0
    for res in (data.get("Results") or []):
        targets += 1
        vulns += len(res.get("Vulnerabilities") or [])
        misconfigs += len(res.get("Misconfigurations") or [])
        # Secrets are reported under "Secrets" list when secret scanner is enabled
        secrets += len(res.get("Secrets") or [])
    return {
        "targets_scanned": targets,
        "vulnerabilities": vulns,
        "misconfigurations": misconfigs,
        "secrets": secrets,
    }

def _summarize_gitleaks(data) -> dict:
    # Gitleaks --report-format json returns a list of findings
    if isinstance(data, list):
        return {"leaks": len(data)}
    if isinstance(data, dict) and "findings" in data:
        return {"leaks": len(data.get("findings") or [])}
    return {"leaks": 0}

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

        trivy_summary = _summarize_trivy(trivy_json) if trivy_rc == 0 else None
        gitleaks_summary = _summarize_gitleaks(gitleaks_json) if gitleaks_rc == 0 else None
        
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

        # Build a clean response
        return {
            "status": "scanned",
            "repo": repo_url,
            "branch": branch,
            "commit": commit,
            "summary": {
                "trivy": trivy_summary,
                "gitleaks": gitleaks_summary,
            },
            "trivy": {
                "returncode": trivy_rc,
                "stderr": trivy_err,
                "json": trivy_json,   # parsed results
            },
            "gitleaks": {
                "returncode": gitleaks_rc,
                "stderr": gitleaks_err,
                "json": gitleaks_json,  # parsed results
            },
        }

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/scan")
async def scan_repo(payload: dict):
    try:
        data = scan_repo_impl(
            repo_url=payload["repo_url"],
            branch=payload.get("branch", "main"),
            commit=payload.get("commit"),
        )
        return data
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    repo_url = payload["repository"]["clone_url"]
    branch = payload["ref"].split("/")[-1]
    commit = payload["after"]

    print(f"Webhook received:\nRepo: {repo_url}\nBranch: {branch}\nCommit: {commit}")

    # Do in background so GitHub gets a fast 200
    background_tasks.add_task(scan_repo_impl, repo_url, branch, commit)
    return {"status": "accepted", "repo": repo_url, "branch": branch, "commit": commit}
