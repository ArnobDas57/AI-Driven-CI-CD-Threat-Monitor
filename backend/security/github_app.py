import hmac, hashlib, time, requests, jwt
from config import GITHUB_WEBHOOK_SECRET, GITHUB_APP_ID, PRIVATE_KEY_OBJ

def verify_signature(body: bytes, sig_header: str) -> bool:
    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, sig_header or "")

def app_jwt() -> str:
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 9 * 60, "iss": GITHUB_APP_ID}
    # PyJWT accepts a cryptography key object directly
    return jwt.encode(payload, PRIVATE_KEY_OBJ, algorithm="RS256")

def installation_token(installation_id: int) -> str:
    token = app_jwt()
    r = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )
    r.raise_for_status()
    return r.json()["token"]
