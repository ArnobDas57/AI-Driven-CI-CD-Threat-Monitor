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

# I think we use this endpoint as a button for users to manually scan when a push is detected
# This button should run trivy and gitleaks for info, then feed it into the LLM
@app.post("/scan")
async def scan_repo(request: Request):
    body = await request.json()
    repo_url = body.get("repo_url")
    # TODO: Run Trivy/Snyk/Semgrep scan logic here
    return {"status": "scanned", "repo": repo_url}

# This should detect a push event from a github thats set up correctly, and gets all the info needed for trivy and gitleaks
@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    repo_url = payload["repository"]["clone_url"]
    branch = payload["ref"].split("/")[-1]
    commit = payload["after"]

    print(f"Webhook received:\nRepo: {repo_url}\nBranch: {branch}\nCommit: {commit}")

    return {"status": "received", "repo": repo_url, "branch": branch, "commit": commit}

