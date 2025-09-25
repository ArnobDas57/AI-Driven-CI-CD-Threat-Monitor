from fastapi import APIRouter, Header
router = APIRouter()

@router.post("")
async def gitlab_webhook(payload: dict, x_gitlab_token: str | None = Header(default=None)):
    # TODO: verify token if configured
    return {"ok": True}
