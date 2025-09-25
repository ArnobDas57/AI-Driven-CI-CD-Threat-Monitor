"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ShieldCheck,
  Activity,
  Cpu,
  BellRing,
  ScanLine,
  GitBranch,
  Github,
  Gitlab,
  LockKeyhole,
  Sparkles,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Feature } from "@/components/Feature/Feature";
import { Step } from "@/components/Step/Step";

export default function Home() {
  const router = useRouter();
  const [repoUrl, setRepoUrl] = React.useState("");

  const goConnectGitHub = () => router.push("/connect/github");
  const goAddWebhook = () => router.push("/onboarding/webhook");
  const goStartScan = () => {
    const q = repoUrl.trim()
      ? `?repo=${encodeURIComponent(repoUrl.trim())}`
      : "";
    router.push(`/scans/new${q}`);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white selection:bg-fuchsia-500/30 selection:text-white">
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute -top-24 -left-24 h-80 w-80 rounded-full bg-fuchsia-600/20 blur-3xl" />
        <div className="absolute -bottom-24 -right-24 h-96 w-96 rounded-full bg-cyan-500/10 blur-[100px]" />
      </div>

      {/* Navbar */}
      <header className="sticky top-0 z-40 border-b border-neutral-900/70 bg-neutral-950/70 backdrop-blur supports-[backdrop-filter]:bg-neutral-950/50">
        <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-fuchsia-600 via-purple-600 to-cyan-500 shadow-lg">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <span className="text-lg font-bold tracking-tight">ThreatLens</span>
            <Badge
              variant="secondary"
              className="ml-2 hidden md:inline-flex bg-neutral-900 border-neutral-800 text-white"
            >
              AI-Driven Threat Monitor for DevSecOps
            </Badge>
          </div>
          <div className="hidden items-center gap-6 md:flex">
            <a
              className="text-sm text-neutral-300 hover:text-white"
              href="#features"
            >
              Features
            </a>
            <a
              className="text-sm text-neutral-300 hover:text-white"
              href="#how"
            >
              How it works
            </a>
            <a
              className="text-sm text-neutral-300 hover:text-white"
              href="#integrations"
            >
              Integrations
            </a>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" asChild className="hidden md:inline-flex">
              <a
                href="https://github.com/ArnobDas57/AI-Driven-CI-CD-Threat-Monitor"
                target="_blank"
                rel="noreferrer"
              >
                <Github className="mr-2 h-4 w-4" /> GitHub
              </a>
            </Button>
            <Button
              onClick={goConnectGitHub}
              className="bg-gradient-to-tr from-fuchsia-600 to-purple-600 hover:from-fuchsia-500 hover:to-purple-500"
            >
              <Github className="mr-2 h-4 w-4" />
              Connect GitHub
            </Button>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-7xl px-4 pt-14">
        <div className="grid gap-10 md:grid-cols-2 md:items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="mt-4 text-4xl font-extrabold leading-tight md:text-5xl lg:text-6xl">
              See threats in your CI/CD{" "}
              <span className="bg-gradient-to-r from-fuchsia-400 to-cyan-300 bg-clip-text text-transparent">
                before they ship
              </span>
            </h1>
            <p className="mt-4 max-w-xl text-neutral-300">
              ThreatLens monitors GitHub Actions & GitLab pipelines, runs
              secret/dependency scans, and uses AI to explain risky behavior in
              plain English—so teams can fix fast and ship safely.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              <Button
                size="lg"
                onClick={goConnectGitHub}
                className="bg-gradient-to-tr from-fuchsia-600 to-purple-600 hover:from-fuchsia-500 hover:to-purple-500"
              >
                <Sparkles className="mr-2 h-4 w-4" /> Connect GitHub
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={goAddWebhook}
                className="border-neutral-800 bg-neutral-950"
              >
                <ScanLine className="mr-2 h-4 w-4" /> Add Webhook
              </Button>
            </div>
            <div className="mt-6 flex flex-wrap items-center gap-3 text-xs text-white">
              <span className="inline-flex items-center gap-1">
                <LockKeyhole className="h-3.5 w-3.5" /> Secret Detection
              </span>
              <span className="inline-flex items-center gap-1">
                <Activity className="h-3.5 w-3.5" /> Anomaly Scoring
              </span>
              <span className="inline-flex items-center gap-1">
                <Cpu className="h-3.5 w-3.5" /> LLM Explanations
              </span>
              <span className="inline-flex items-center gap-1">
                <BellRing className="h-3.5 w-3.5" /> Slack Alerts
              </span>
            </div>
          </motion.div>

          {/* Right: Preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="relative"
          >
            <div className="absolute -inset-1 rounded-3xl bg-gradient-to-tr from-fuchsia-600/30 via-purple-600/20 to-cyan-500/20 blur-2xl" />
            <div className="relative rounded-3xl border border-neutral-800 bg-neutral-900/60 p-4 shadow-2xl backdrop-blur">
              <div className="flex items-center justify-between rounded-2xl border border-neutral-800 bg-neutral-950 px-3 py-2">
                <div className="flex items-center gap-2 text-xs text-neutral-300">
                  <div className="h-2 w-2 rounded-full bg-green-400" />
                  Pipeline • main • build #412
                </div>
                <Badge
                  variant="secondary"
                  className="bg-green-500/15 text-green-300 border-green-700/40"
                >
                  Risk 2/10
                </Badge>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <Card className="border-neutral-800 bg-neutral-950">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm text-neutral-300">Findings</CardTitle>
                    <CardDescription>Last run • 2m ago</CardDescription>
                  </CardHeader>
                  <CardContent className="text-sm text-neutral-300">
                    <ul className="space-y-2">
                      <li className="flex items-start gap-2">
                        <LockKeyhole className="mt-0.5 h-4 w-4 text-fuchsia-400" />{" "}
                        No hardcoded secrets detected
                      </li>
                      <li className="flex items-start gap-2">
                        <Activity className="mt-0.5 h-4 w-4 text-cyan-300" />{" "}
                        Dependencies clean (0 critical CVEs)
                      </li>
                      <li className="flex items-start gap-2">
                        <BellRing className="mt-0.5 h-4 w-4 text-purple-300" />{" "}
                        Policy: all prod deploys within hours
                      </li>
                    </ul>
                  </CardContent>
                </Card>
                <Card className="border-neutral-800 bg-neutral-950">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm text-neutral-300">AI Summary</CardTitle>
                    <CardDescription>English, actionable</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-neutral-300">
                      “Build looks healthy. Keep artifact scanning enabled.
                      Consider pinning <code>actions/checkout</code> to a commit
                      SHA for supply-chain hardening.”
                    </p>
                  </CardContent>
                </Card>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-neutral-400">
                  <GitBranch className="h-4 w-4" />
                  <span>
                    github.com/org/repo •{" "}
                    <span className="text-neutral-300">a1b2c3d</span>
                  </span>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  className="border-neutral-800 bg-neutral-950"
                >
                  View full report <ChevronRight className="ml-1 h-4 w-4" />
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Integrations */}
      <section id="integrations" className="mx-auto mt-16 max-w-7xl px-4">
        <div className="rounded-3xl border border-neutral-900 bg-neutral-950/40 p-6">
          <p className="mb-4 text-center text-2xl font-bold">Integrates with</p>
          <div className="flex flex-wrap items-center justify-center gap-6 text-neutral-300">
            <span className="inline-flex items-center gap-2 rounded-xl border border-neutral-800 bg-neutral-900 px-3 py-2 text-sm">
              <Github className="h-4 w-4" /> GitHub Actions
            </span>
            <span className="inline-flex items-center gap-2 rounded-xl border border-neutral-800 bg-neutral-900 px-3 py-2 text-sm">
              <Gitlab className="h-4 w-4" /> GitLab CI
            </span>
            <span className="inline-flex items-center gap-2 rounded-xl border border-neutral-800 bg-neutral-900 px-3 py-2 text-sm">
              <BellRing className="h-4 w-4" /> Slack / Email
            </span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto mt-16 max-w-7xl px-4">
        <div className="justify-center flex mb-6">
          <h1 className="text-2xl font-bold">Core Features</h1>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          <Feature
            icon={LockKeyhole}
            title="Secret Detection"
            desc="Scan code, envs, and build logs for API keys, tokens, and credentials using Gitleaks."
          />
          <Feature
            icon={Activity}
            title="Dependency & Image Scanning"
            desc="Surface CVEs in package manifests and Dockerfiles with Trivy."
          />
          <Feature
            icon={BellRing}
            title="Policy Guardrails"
            desc="Block risky deploys outside business hours. Enforce branch protections and required checks."
          />
          <Feature
            icon={Cpu}
            title="AI Explanations"
            desc="LLM-generated summaries convert noisy logs into clear, actionable guidance."
          />
          <Feature
            icon={ScanLine}
            title="Anomaly Detection"
            desc="Score unusual commit patterns, log spikes, or permission escalations."
          />
          <Feature
            icon={ShieldCheck}
            title="Threat Scoring"
            desc="Simple 1–10 risk scores with context and recommended mitigations."
          />
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="mx-auto mt-20 max-w-7xl px-4">
        <div className="grid gap-10 lg:grid-cols-2">
          <div>
            <h2 className="text-2xl font-bold">How ThreatLens works</h2>
            <p className="mt-2 text-neutral-300">
              Webhooks trigger scans, AI explains results, and your team gets
              concise alerts with clear next steps.
            </p>
            <div className="mt-6 space-y-5">
              <Step
                n={1}
                title="Webhook → Backend"
                desc="Receive GitHub/GitLab events with repo, branch, and commit metadata."
              />
              <Step
                n={2}
                title="Static Analysis"
                desc="Run Gitleaks + Trivy; normalize JSON output and enrich with metadata."
              />
              <Step
                n={3}
                title="LLM Summaries"
                desc="Generate plain-English context: risk score, what happened, what to fix."
              />
              <Step
                n={4}
                title="Alerting + Block"
                desc="Send Slack/email alerts with severity; optionally fail the pipeline when critical."
              />
              <Step
                n={5}
                title="History + Dashboard"
                desc="Persist runs to Postgres; visualize trends and incidents over time."
              />
            </div>
          </div>
          <div className="rounded-3xl border border-neutral-900 bg-neutral-950/40 p-6">
            <h3 className="text-lg font-semibold">Quick start</h3>
            <p className="mt-1 text-sm text-neutral-300">
              Add a repository to begin monitoring.
            </p>
            <div className="mt-4 flex flex-col gap-3 sm:flex-row">
              <Input
                placeholder="https://github.com/owner/repo"
                className="bg-neutral-900 border-neutral-800"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
              />
              <Button
                className="bg-gradient-to-tr from-fuchsia-600 to-purple-600 hover:from-fuchsia-500 hover:to-purple-500"
                onClick={goStartScan}
              >
                Start Scan <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            </div>
            <div className="mt-6 grid gap-3 md:grid-cols-2">
              <Card className="border-neutral-800 bg-neutral-900">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm text-neutral-300">
                    What you get
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-neutral-300">
                  • Findings JSON <br />• AI summary <br />• Risk score <br />•
                  Suggested fixes
                </CardContent>
              </Card>
              <Card className="border-neutral-800 bg-neutral-900">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm text-neutral-300">
                    Under the hood
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-neutral-300">
                  Gitleaks, Trivy, FastAPI/Express, OpenAI API, Postgres/SQLite
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto mt-16 max-w-7xl px-4">
        <div className="relative overflow-hidden rounded-3xl border border-neutral-900 bg-gradient-to-tr from-neutral-950 via-neutral-900 to-neutral-900 p-8">
          <div className="absolute -right-10 -top-24 h-64 w-64 rounded-full bg-fuchsia-600/20 blur-3xl" />
          <div className="absolute -bottom-20 -left-10 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />
          <div className="relative grid gap-6 md:grid-cols-2 md:items-center">
            <div>
              <h3 className="text-2xl font-bold">
                Ready to put your pipelines on watch?
              </h3>
              <p className="mt-2 text-neutral-300">
                Connect your GitHub and add a webhook to start real monitoring.
              </p>
            </div>
            <div className="flex gap-3 md:justify-end">
              <Button
                size="lg"
                onClick={goConnectGitHub}
                className="bg-gradient-to-tr from-fuchsia-600 to-purple-600 hover:from-fuchsia-500 hover:to-purple-500"
              >
                Add Repository
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-neutral-800 bg-neutral-950"
                onClick={goAddWebhook}
              >
                Add Webhook
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mx-auto mt-16 max-w-7xl px-4 pb-10">
        <div className="flex flex-col items-center justify-between gap-4 border-t border-neutral-900 pt-6 md:flex-row">
          <div className="flex items-center gap-2 text-sm text-neutral-400">
            <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-gradient-to-tr from-fuchsia-600 via-purple-600 to-cyan-500">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <span>
              ThreatLens © {new Date().getFullYear()} Built by Tommy Le and
              Arnob Das
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
