# SETTING UP BACKEND
import datetime
import logging
import os
import shutil
import subprocess
import tempfile

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

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


# Helper function for running scanners
async def run_scanners(temp_dir: str):
    try:
        trivy_result = subprocess.run(
            ["trivy", "fs", temp_dir], capture_output=True, text=True, check=True
        )
        gitleaks_result = subprocess.run(
            ["gitleaks", "detect", "--source", temp_dir, "--report-format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"Scanner subprocess failed: {e}")
        raise

    return {
        "trivy_output": trivy_result.stdout,
        "gitleaks_output": gitleaks_result.stdout,
    }


@app.post("/scan")
async def scan_repo(payload: dict):
    repo_url = payload.get("repo_url")
    branch = payload.get("branch", "main")

    if not repo_url:
        raise HTTPException(status_code=400, detail="repo_url is required")

    temp_dir = tempfile.mkdtemp()
    logging.info(f"Starting scan for repo {repo_url} on branch {branch}")

    try:
        # Clone Git repo (specific branch if provided)
        subprocess.run(
            ["git", "clone", "--branch", branch, repo_url, temp_dir],
            check=True,
            capture_output=True,
            text=True,
        )
        logging.info("Repo cloned successfully")

        # Run Trivy & Gitleaks scanners
        scan_outputs = await run_scanners(temp_dir)
        logging.info("Scanning completed successfully")

        return {
            "status": "scanned",
            "repo": repo_url,
            "branch": branch,
            "trivy_output": scan_outputs["trivy_output"],
            "gitleaks_output": scan_outputs["gitleaks_output"],
            "scan_time": str(datetime.datetime.utcnow()),
        }

    except subprocess.CalledProcessError as e:
        logging.error(f"Subprocess failed: {e}")
        return JSONResponse(
            status_code=500, content={"error": f"Subprocess failed: {e}"}
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500, content={"error": f"Unexpected error: {str(e)}"}
        )
    finally:
        shutil.rmtree(temp_dir)
        logging.info(f"Cleaned up temporary directory {temp_dir}")


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

    return {"status": "received", "repo": repo_url, "branch": branch, "commit": commit}
