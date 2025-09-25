from fastapi import APIRouter, Header
router = APIRouter()

@router.post("")
async def github_webhook(payload: dict, x_hub_signature_256: str | None = Header(default=None)):
    # TODO: verify HMAC if you configure a secret
    # TODO: enqueue or trigger follow-up logic if you want event-driven flows
    return {"ok": True}
