import subprocess, json
from pathlib import Path

def run_cmd(cmd, cwd=None, check=True, env=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env, check=check)
        return (p.returncode, p.stdout, p.stderr)
    except FileNotFoundError as e:
        raise RuntimeError(f"Command not found: {cmd[0]}") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nexit={e.returncode}\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}") from e

def _safe_json_loads(s: str, default):
    try: return json.loads(s)
    except Exception: return default

def _mask(s: str | None, keep_start=4, keep_end=2):
    if not s: return s
    n = len(s)
    if n <= keep_start + keep_end: return "*" * n
    return s[:keep_start] + "*" * (n - keep_start - keep_end) + s[-keep_end:]

def _read_snippet(root: str, rel_file: str | None, line: int | None, ctx=2):
    if not rel_file or not line: return None
    try:
        p = Path(root) / rel_file
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        line = int(line); s = max(1, line - ctx); e = min(len(lines), line + ctx)
        return {"start_line": s, "end_line": e, "code": "\n".join(lines[s-1:e])}
    except Exception:
        return None
