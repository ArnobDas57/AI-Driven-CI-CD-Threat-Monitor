from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Any, Optional
import os

router = APIRouter()
API_KEY = os.getenv("OPENAI_API_KEY", "")

class IngestPayload(BaseModel):
    repo: str
    branch: str
    commit: str
    gitleaks: Optional[Any] = None
    trivy: Optional[Any] = None

def compute_risk(gitleaks, trivy) -> int:
    risk = 1
    # secrets (gitleaks)
    try:
        leaks = len(gitleaks or []) if isinstance(gitleaks, list) else len((gitleaks or {}).get("findings", []))
        if leaks > 0:
            risk = max(risk, 8)
    except:
        pass

    # CVEs (trivy)
    try:
        results = (trivy or {}).get("Results", [])
        vulns = [v for r in results for v in (r.get("Vulnerabilities") or [])]
        if any(v.get("Severity") == "CRITICAL" for v in vulns):
            risk = max(risk, 8)
        elif vulns:
            risk = max(risk, 6)
    except:
        pass

    return min(risk, 10)

@router.post("")
async def ingest_github(payload: IngestPayload, authorization: str = Header("")):
    token = authorization.replace("Bearer ", "")
    if API_KEY and token != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    risk = compute_risk(payload.gitleaks, payload.trivy)
    
    # TODO: persist to DB, send Slack if threshold met
    return {"ok": True, "risk_score": risk, "repo": payload.repo, "commit": payload.commit}
