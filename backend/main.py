# main.py (API)
import os, shutil, tempfile, subprocess, datetime, json, logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from rq import Queue
from redis import Redis
from uuid import uuid4

load_dotenv()
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

# Redis (use REDIS_URL in cloud, e.g. Upstash/Redis Cloud)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(REDIS_URL)
q = Queue("scans", connection=redis_conn)


@app.get("/")
def root():
    return {"message": "AI-Driven CI/CD Threat Monitor backend is up and running 🚀"}


@app.post("/scan", status_code=202)
def create_scan(payload: dict):
    repo_url = payload.get("repo_url")
    branch = payload.get("branch", "main")
    if not repo_url:
        raise HTTPException(status_code=400, detail="repo_url is required")

    # Create a job id so clients can poll without waiting
    job_id = str(uuid4())
    logging.info(f"Enqueuing scan: {repo_url} (branch={branch}, job_id={job_id})")

    # Enqueue background work in the worker container
    q.enqueue(
        "worker.run_scan_job",
        job_id,
        repo_url,
        branch,
        job_timeout=60 * 15,  # 15m hard limit
        result_ttl=60 * 60 * 24,  # keep result 24h
    )
    return {"status": "queued", "job_id": job_id, "status_url": f"/scans/{job_id}"}


@app.get("/scans/{job_id}")
def get_scan_status(job_id: str):
    data = redis_conn.get(f"scan:{job_id}")
    if not data:
        # Could be queued/running or unknown
        state = redis_conn.get(f"scan:{job_id}:state")
        if state:
            return {"job_id": job_id, "state": state.decode()}
        return JSONResponse(status_code=404, content={"error": "job not found"})
    result = json.loads(data)
    return result
