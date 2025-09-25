import shutil, tempfile
from datetime import datetime, timezone
from utils.shell import run_cmd, _safe_json_loads
from scanner.summarize import _summarize_trivy, _summarize_gitleaks
from utils.shell import _mask


def build_llm_payload(
    repo_url: str,
    branch: str,
    commit: str,
    temp_dir: str,
    trivy_json: dict,
    gitleaks_json,
) -> dict:
    findings = []
    findings += _summarize_trivy(trivy_json, temp_dir)
    findings += _summarize_gitleaks(gitleaks_json, temp_dir)

    for f in findings:
        if "evidence" in f and isinstance(f["evidence"], str):
            f["evidence"] = _mask(f["evidence"], keep_start=4, keep_end=2)

    return {
        "repo": repo_url,
        "branch": branch,
        "commit": commit,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "findings": findings,
    }


def scan_repo_impl(
    repo_url: str, branch: str = "main", commit: str | None = None
) -> dict:
    temp_dir = tempfile.mkdtemp(prefix="scan-")
    try:
        if commit:
            run_cmd(["git", "clone", "--no-checkout", repo_url, temp_dir])
            run_cmd(["git", "fetch", "--depth", "1", "origin", commit], cwd=temp_dir)
            run_cmd(["git", "checkout", commit], cwd=temp_dir)
        else:
            run_cmd(
                ["git", "clone", "--depth", "1", "--branch", branch, repo_url, temp_dir]
            )

        trivy_rc, trivy_out, trivy_err = run_cmd(
            [
                "trivy",
                "fs",
                "--no-progress",
                "--format",
                "json",
                "--scanners",
                "vuln,secret,misconfig",
                temp_dir,
            ],
            check=False,
        )
        gitleaks_rc, gitleaks_out, gitleaks_err = run_cmd(
            [
                "gitleaks",
                "detect",
                "--source",
                temp_dir,
                "--report-format",
                "json",
                "--no-banner",
            ],
            check=False,
        )

        trivy_json = _safe_json_loads(trivy_out or "{}", {})
        gitleaks_json = _safe_json_loads(gitleaks_out or "[]", [])

        llm_input = build_llm_payload(
            repo_url, branch, commit, temp_dir, trivy_json, gitleaks_json
        )

        return {
            "status": "scanned",
            "repo": repo_url,
            "branch": branch,
            "commit": commit,
            "summary": {
                "trivy": _summarize_trivy(trivy_json, temp_dir)
                and {
                    "counts": {
                        "targets_scanned": len(trivy_json.get("Results") or []),
                        "vulnerabilities": sum(
                            len(r.get("Vulnerabilities") or [])
                            for r in (trivy_json.get("Results") or [])
                        ),
                        "misconfigurations": sum(
                            len(r.get("Misconfigurations") or [])
                            for r in (trivy_json.get("Results") or [])
                        ),
                        "secrets": sum(
                            len(r.get("Secrets") or [])
                            for r in (trivy_json.get("Results") or [])
                        ),
                    }
                },
                "gitleaks": {
                    "leaks": len(llm_input["findings"])
                    - sum(
                        len(r.get("Vulnerabilities") or [])
                        + len(r.get("Misconfigurations") or [])
                        + len(r.get("Secrets") or [])
                        for r in (trivy_json.get("Results") or [])
                    )
                },
            },
            "llm_input": llm_input,
            "trivy": {"returncode": trivy_rc, "stderr": trivy_err, "json": trivy_json},
            "gitleaks": {
                "returncode": gitleaks_rc,
                "stderr": gitleaks_err,
                "json": gitleaks_json,
            },
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
