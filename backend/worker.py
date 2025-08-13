# worker.py (Worker)
import os, json, tempfile, shutil, subprocess, datetime, logging
from redis import Redis
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(REDIS_URL)


def _safe_run(cmd: list[str], timeout: int = 600) -> tuple[int, str, str]:
    # Return (code, stdout, stderr) without raising, to capture scanner failures gracefully
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def run_scan_job(job_id: str, repo_url: str, branch: str = "main"):
    state_key = f"scan:{job_id}:state"
    result_key = f"scan:{job_id}"
    redis_conn.set(state_key, "running")

    temp_dir = tempfile.mkdtemp()
    try:
        # Shallow, blobless clone (fast + low bandwidth)
        clone_cmd = [
            "git",
            "clone",
            "--depth",
            "1",
            "--filter=blob:none",
            "--branch",
            branch,
            repo_url,
            temp_dir,
        ]
        code, out, err = _safe_run(clone_cmd, timeout=300)
        if code != 0:
            result = {
                "job_id": job_id,
                "state": "failed",
                "error_type": "git_clone",
                "repo": repo_url,
                "branch": branch,
                "stderr": err,
                "stdout": out,
            }
            redis_conn.set(result_key, json.dumps(result))
            redis_conn.set(state_key, "failed")
            return

        # Trivy (filesystem mode). Use a cached DB dir if you mount one.
        trivy_cmd = ["trivy", "fs", temp_dir, "--scanners", "vuln,misconfig,secret"]
        t_code, t_out, t_err = _safe_run(trivy_cmd, timeout=600)

        # Gitleaks
        gitleaks_cmd = [
            "gitleaks",
            "detect",
            "--source",
            temp_dir,
            "--report-format",
            "json",
        ]
        g_code, g_out, g_err = _safe_run(gitleaks_cmd, timeout=600)

        status = (
            "completed"
            if (t_code == 0 and g_code in (0, 1))
            else "completed_with_findings_or_errors"
        )
        # Note: Gitleaks returns 1 when leaks are found; treat that as "completed" with findings.

        result = {
            "job_id": job_id,
            "state": status,
            "repo": repo_url,
            "branch": branch,
            "scan_time": datetime.datetime.utcnow().isoformat() + "Z",
            "trivy": {"exit_code": t_code, "stdout": t_out, "stderr": t_err},
            "gitleaks": {"exit_code": g_code, "stdout": g_out, "stderr": g_err},
        }
        redis_conn.set(result_key, json.dumps(result))
        redis_conn.set(state_key, status)
    except subprocess.TimeoutExpired as e:
        result = {
            "job_id": job_id,
            "state": "failed",
            "error_type": "timeout",
            "repo": repo_url,
            "branch": branch,
            "detail": str(e),
        }
        redis_conn.set(result_key, json.dumps(result))
        redis_conn.set(state_key, "failed")
    except Exception as e:
        result = {
            "job_id": job_id,
            "state": "failed",
            "error_type": "exception",
            "repo": repo_url,
            "branch": branch,
            "detail": str(e),
        }
        redis_conn.set(result_key, json.dumps(result))
        redis_conn.set(state_key, "failed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
