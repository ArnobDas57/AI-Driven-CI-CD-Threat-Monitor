from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, AnyUrl
from typing import Optional
from fastapi.responses import JSONResponse
from scanner.scan import scan_repo_impl

router = APIRouter()

class ScanRequest(BaseModel):
    repo_url: AnyUrl
    branch: Optional[str] = "main"
    commit: Optional[str] = None

@router.post("")
async def scan(req: ScanRequest):
    # TODO: clone shallow, run gitleaks/trivy (for backend-run scans)
    # return a fake response for now so UI works end-to-end
    return {
        "ok": True,
        "repo_url": str(req.repo_url),
        "branch": req.branch,
        "commit": req.commit,
        "summary": "Sample response (wire real scanners next).",
        "risk_score": 2
    }

@router.post("/scan")
async def scan_handler(payload: dict):
    try:
        data = scan_repo_impl(
            repo_url=payload["repo_url"],
            branch=payload.get("branch","main"),
            commit=payload.get("commit"),
        )
        return data
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# THIS NEEDS TO BE UPDATED TO MATCH AUTHORIZATION LIKE IN THE WEBHOOK/GITHUB ROUTES OR BE DELETED