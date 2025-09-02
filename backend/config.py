from pathlib import Path
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
import os

# backend/config.py is inside backend/, project root is one level up
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

GITHUB_WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"].strip().strip('"').strip("'")
GITHUB_APP_ID = os.environ["GITHUB_APP_ID"].strip()

# Load PEM from file if provided (recommended), else from env with \n escapes
key_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
if key_path:
    pem = (ROOT / key_path).read_text(encoding="utf-8")
else:
    pem = os.environ["GITHUB_APP_PRIVATE_KEY"].replace("\\n", "\n")

# Parse/validate once at startup; raise if broken
PRIVATE_KEY_OBJ = serialization.load_pem_private_key(pem.encode("utf-8"), password=None)

# --- OpenAI / LLM ---
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"].strip()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
LLM_MAX_FINDINGS = int(os.getenv("LLM_MAX_FINDINGS", "150"))
LLM_MAX_EVIDENCE_CHARS = int(os.getenv("LLM_MAX_EVIDENCE_CHARS", "800"))