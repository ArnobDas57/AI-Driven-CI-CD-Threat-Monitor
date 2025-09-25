from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    LLM_MAX_FINDINGS,
    LLM_MAX_EVIDENCE_CHARS,
)

# ---------- schema the model should return ----------
class Threat(BaseModel):
    id: str = Field(..., description="Stable ID for the issue (e.g., TRIVY-<target>-<idx> or GITLEAKS-<file>-<line>)")
    title: str
    severity: int = Field(..., ge=0, le=10)
    file: Optional[str] = None
    evidence: Optional[str] = None
    remediation: Optional[str] = None

class Analysis(BaseModel):
    summary: str
    risk_score: int = Field(..., ge=0, le=10)
    top_threats: List[Threat]
    fix_plan: List[str]

# ---------- small helpers ----------
def _truncate_findings(findings: List[dict]) -> List[dict]:
    out = []
    for f in findings[:LLM_MAX_FINDINGS]:
        f = dict(f)
        ev = f.get("evidence")
        if isinstance(ev, str) and len(ev) > LLM_MAX_EVIDENCE_CHARS:
            f["evidence"] = ev[:LLM_MAX_EVIDENCE_CHARS] + "..."
        out.append(f)
    return out

def _build_prompt(scan: Dict[str, Any]) -> ChatPromptTemplate:
    """
    Keep the prompt compact: give model only what's needed.
    scan['llm_input'] should already have normalized fields.
    """
    template = """You are a security triage assistant for CI/CD scans.

Repo: {repo}
Branch: {branch}
Commit: {commit}

You will receive normalized findings from tools like Trivy (vuln/misconfig/secret) and Gitleaks.
Produce a concise, prioritized analysis strictly following the requested schema.

Guidelines:
- Be precise and actionable.
- Use 0–10 severity and overall risk_score (0=no risk; 10=critical).
- Limit top_threats to the most impactful (up to ~10). Prefer coverage over duplication.
- fix_plan should be ordered, concrete steps a developer can follow.

Findings (truncated for cost):
{findings_json}
"""
    return ChatPromptTemplate.from_template(template)

# ---------- main entrypoint you’ll call from pipeline ----------
def analyze_with_llm(scan_result: Dict[str, Any], *, model_name: Optional[str] = None) -> Dict[str, Any]:
    llm_input = scan_result.get("llm_input") or {}
    repo, branch, commit = llm_input.get("repo"), llm_input.get("branch"), llm_input.get("commit")
    findings = _truncate_findings(llm_input.get("findings") or [])

    prompt = _build_prompt({ "repo": repo, "branch": branch, "commit": commit, "findings_json": findings, })

    llm = ChatOpenAI(
        model=model_name or OPENAI_MODEL,
        temperature=0.1,
        api_key=OPENAI_API_KEY,
    )

    runnable = prompt | llm.with_structured_output(Analysis)

    try:
        analysis: Analysis = runnable.invoke({
            "repo": repo, "branch": branch, "commit": commit, "findings_json": findings
        })
        return analysis.model_dump()
    except Exception as e:
        return {
            "error": f"llm_analysis_failed: {e.__class__.__name__}: {e}",
            "summary": "LLM analysis failed; showing raw scan only.",
            "risk_score": 0,
            "top_threats": [],
            "fix_plan": [],
        }

