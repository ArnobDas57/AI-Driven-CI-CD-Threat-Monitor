# backend/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env explicitly
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

def env_str(name: str, default: str = "") -> str:
    val = os.getenv(name, default)
    return (val or "").strip().strip('"').strip("'")

def env_int(name: str, default: int = 0) -> int:
    try:
        return int(env_str(name, str(default)))
    except ValueError:
        return default

# --- Required-but-safe (no KeyError) ---
THREATLENS_API_KEY = env_str("THREATLENS_API_KEY", "")

GITHUB_WEBHOOK_SECRET = env_str("GITHUB_WEBHOOK_SECRET", "")
GITHUB_APP_ID = env_str("GITHUB_APP_ID", "")
GITHUB_APP_PRIVATE_KEY_PATH = env_str("GITHUB_APP_PRIVATE_KEY_PATH", "")

OPENAI_API_KEY = env_str("OPENAI_API_KEY", "")
OPENAI_MODEL = env_str("OPENAI_MODEL", "gpt-4o-mini")
LLM_MAX_FINDINGS = env_int("LLM_MAX_FINDINGS", 150)
LLM_MAX_EVIDENCE_CHARS = env_int("LLM_MAX_EVIDENCE_CHARS", 800)

FRONTEND_ORIGIN = env_str("FRONTEND_ORIGIN", "http://localhost:3000")
VERCEL_ORIGIN = env_str("VERCEL_ORIGIN", "")
CORS_ORIGINS = [o for o in [FRONTEND_ORIGIN, VERCEL_ORIGIN] if o]

SLACK_WEBHOOK_URL = env_str("SLACK_WEBHOOK_URL", "")

# Helper: read GitHub App private key only if needed
def read_github_app_private_key() -> str | None:
    p = GITHUB_APP_PRIVATE_KEY_PATH
    if not p:
        return None
    path = Path(p)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")
