from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scanner.scan import scan_repo_impl

router = APIRouter()

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