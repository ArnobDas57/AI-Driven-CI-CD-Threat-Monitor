# SETTING UP BACKEND
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "AI-Driven CI/CD Threat Monitor backend is up and running 🚀"}


@app.post("/scan")
async def scan_repo(request: Request):
    body = await request.json()
    repo_url = body.get("repo_url")
    # TODO: Run Trivy/Snyk/Semgrep scan logic here
    return {"status": "scanned", "repo": repo_url}
