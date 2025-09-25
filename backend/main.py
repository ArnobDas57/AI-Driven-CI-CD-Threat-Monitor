from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGINS

from api.webhooks import router as webhooks_router
from api.scan import router as scan_router
from api.ingest.github import router as ingest_router
from api.webhook.github import router as github_webhook_router
from api.webhook.gitlab import router as gitlab_webhook_router

app = FastAPI()
app.include_router(webhooks_router)
app.include_router(scan_router)

app = FastAPI(title="ThreatLens API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in CORS_ORIGINS if o],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "ThreatLens backend is up 🚀"}

app.include_router(ingest_router, prefix="/ingest/github", tags=["ingest"])
app.include_router(github_webhook_router, prefix="/webhook/github", tags=["webhook"])
app.include_router(gitlab_webhook_router, prefix="/webhook/gitlab", tags=["webhook"])
app.include_router(scan_router, prefix="/scan", tags=["scan"])
