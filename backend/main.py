# SETTING UP BACKEND
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import tempfile
import subprocess
import shutil

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
async def scan_repo(payload: dict):
    repo_url = payload["repo_url"]
    branch = payload.get("branch", "main")
    commit = payload.get("commit")

    # Clone github repo into temporary folder
    temp_dir = tempfile.mkdtemp()
    subprocess.run(["git", "clone", repo_url, temp_dir], check=True)

    # Run Trivy and GitLeaks on cloned repo
    try:
        # Run Trivy first
        trivy_result = subprocess.run(
            ["trivy", "fs", temp_dir], capture_output=True, text=True
        )

        gitleaks_result = subprocess.run(
            ["gitleaks", "detect", "--source", temp_dir, "--report-format", "json"],
            capture_output=True,
            text=True,
        )

        return {
            "status": "scanned",
            "repo": repo_url,
            "trivy_output": trivy_result.stdout,
            "gitleaks_output": gitleaks_result.stdout,
        }

    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        # Remove the temporary directory
        shutil.rmtree(temp_dir)


@app.post("/llm")
async def llm_response(request: Request):
    # Langchain and Open AI analysis (NEXT STEP)
    return ""


# This should detect a push event from a github thats set up correctly, and gets all the info needed for trivy and gitleaks
@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    repo_url = payload["repository"]["clone_url"]
    branch = payload["ref"].split("/")[-1]
    commit = payload["after"]

    print(f"Webhook received:\nRepo: {repo_url}\nBranch: {branch}\nCommit: {commit}")

    # Trigger the scan route after webhook is created
    client = TestClient(app)
    client.post(
        "/scan", json={"repo_url": repo_url, "branch": branch, "commit": commit}
    )

    return {"status": "received", "repo": repo_url, "branch": branch, "commit": commit}
