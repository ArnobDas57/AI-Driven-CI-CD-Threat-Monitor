from scanner.scan import scan_repo_impl
from scanner.llm import analyze_with_llm

def run_scan_and_analyze(repo_url: str, branch: str = "main", commit: str | None = None) -> dict:
    scan = scan_repo_impl(repo_url, branch, commit)
    analysis = analyze_with_llm(scan)

    # ✅ Debug print — just to verify in console/logs
    print("[pipeline] LLM analysis result:")
    print(analysis)

    return {"scan": scan, "analysis": analysis}