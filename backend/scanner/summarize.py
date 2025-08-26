from utils.shell import _mask, _read_snippet

def _summarize_trivy(trivy_json: dict, temp_dir: str):
    findings = []
    for res in (trivy_json.get("Results") or []):
        target = res.get("Target")
        for sec in (res.get("Secrets") or []):
            findings.append({
                "tool":"trivy","type":"secret","rule_id":sec.get("RuleID"),
                "title": sec.get("Title") or sec.get("RuleID"),
                "severity": sec.get("Severity") or "UNKNOWN","file": target,
                "start_line": sec.get("StartLine"),"end_line": sec.get("EndLine"),
                "match": _mask(sec.get("Match")),
                "snippet": _read_snippet(temp_dir, target, sec.get("StartLine")),
            })
        for v in (res.get("Vulnerabilities") or []):
            findings.append({
                "tool":"trivy","type":"vulnerability","cve": v.get("VulnerabilityID"),
                "pkg": v.get("PkgName"),"installed": v.get("InstalledVersion"),
                "fixed": v.get("FixedVersion"),"severity": v.get("Severity"),
                "description": v.get("Description"),"primary_url": v.get("PrimaryURL"),
                "file": target,
            })
        for m in (res.get("Misconfigurations") or []):
            cm = m.get("CauseMetadata") or {}
            findings.append({
                "tool":"trivy","type":"misconfiguration","id": m.get("ID"),
                "title": m.get("Title"),"severity": m.get("Severity"),
                "description": m.get("Description"),"message": m.get("Message"),
                "resolution": m.get("Resolution"),"file": target,
                "start_line": (cm.get("StartLine") or cm.get("StartLineNumber")),
                "end_line": (cm.get("EndLine") or cm.get("EndLineNumber")),
                "snippet": _read_snippet(temp_dir, target, cm.get("StartLine") or cm.get("StartLineNumber")),
            })
    return findings

def _summarize_gitleaks(gitleaks_json, temp_dir: str):
    items = gitleaks_json if isinstance(gitleaks_json, list) else (gitleaks_json.get("findings") or [])
    findings = []
    for f in items:
        findings.append({
            "tool":"gitleaks","type":"secret",
            "rule_id": f.get("RuleID") or f.get("Rule"),
            "description": f.get("Description"),
            "file": f.get("File") or f.get("FilePath"),
            "start_line": f.get("StartLine"),"end_line": f.get("EndLine"),
            "secret": _mask(f.get("Secret") or f.get("Match")),
            "entropy": f.get("Entropy"),"tags": f.get("Tags"),
            "snippet": _read_snippet(temp_dir, f.get("File") or f.get("FilePath"), f.get("StartLine")),
        })
    return findings
