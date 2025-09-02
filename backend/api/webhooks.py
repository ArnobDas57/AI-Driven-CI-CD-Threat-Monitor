from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import json
from security.github_app import verify_signature, installation_token
from scanner.pipeline import run_scan_and_analyze

router = APIRouter()

@router.post("/webhook/github")
async def handle_github_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    if not verify_signature(body, request.headers.get("X-Hub-Signature-256","")):
        return JSONResponse(status_code=401, content={"error": "bad signature"})

    event = request.headers.get("X-GitHub-Event","")
    if event == "ping":
        return {"ok": True, "pong": True}
    if event not in ("push","pull_request"):
        return {"ignored": True, "event": event}

    payload = json.loads(body)
    owner = payload["repository"]["owner"]["login"]
    repo  = payload["repository"]["name"]

    if event == "push":
        branch = payload["ref"].split("/")[-1]
        commit = payload["after"]
    else:
        branch = payload["pull_request"]["head"]["ref"]
        commit = payload["pull_request"]["head"]["sha"]

    inst_id = payload["installation"]["id"]
    token = installation_token(inst_id)
    repo_url = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"

    print(f"[webhook] {owner}/{repo}@{branch} {commit[:7]} (inst {inst_id})")
    background_tasks.add_task(run_scan_and_analyze, repo_url, branch, commit)
    return {"status": "accepted", "owner": owner, "repo": repo, "branch": branch, "commit": commit}
