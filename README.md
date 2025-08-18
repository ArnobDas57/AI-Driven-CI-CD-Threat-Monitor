# AI-Driven-CI-CD-Threat-Monitor
Built for DevSecOps teams, this platform monitors GitHub Actions or GitLab pipelines and uses an LLM to translate vulnerabilities, misconfigurations, or suspicious behaviours into plain English explanations. Ideal for early-stage startups and security-focused teams that need real-time security insights.

## 🧱 Core Features ##
🔐 Security Monitoring
- Secret Detection: API keys, tokens, passwords pushed to repo or environment
- Dependency Scanning: CVEs (Common Vulnerabilities and Exposures) in package.json, requirements.txt, etc.
- Policy Violations: E.g., deployments to prod outside business hours

📈 AI-Driven Threat Detection
- Train or use a model to detect anomalies in:
- Commit messages
- Code changes
- Deployment logs
- User behaviour

🚨 Alerting & Blocking
- Slack/Discord/email alerts
- Optionally block builds/deploys
- Threat scoring (e.g., 1–10)

