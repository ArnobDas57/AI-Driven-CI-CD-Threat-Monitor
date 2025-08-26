from fastapi import FastAPI
from api.webhooks import router as webhooks_router
from api.scan import router as scan_router

app = FastAPI()
app.include_router(webhooks_router)
app.include_router(scan_router)
