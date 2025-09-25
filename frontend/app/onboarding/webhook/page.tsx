"use client";
import React from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Copy, LinkIcon, ShieldCheck } from "lucide-react";

export default function WebhookOnboardingPage() {
  const backend =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
  const ghUrl = `${backend}/webhook/github`;
  const glUrl = `${backend}/webhook/gitlab`;

  const copy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      alert("Copied to clipboard");
    } catch {
      alert("Copy failed. Select & copy manually.");
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <div className="mx-auto max-w-3xl px-4 py-10">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-fuchsia-600 via-purple-600 to-cyan-500">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <h1 className="text-2xl font-bold">Add Webhook</h1>
        </div>

        <Card className="border-neutral-900 bg-neutral-950/60">
          <CardHeader>
            <CardTitle className="text-white">GitHub Actions</CardTitle>
            <CardDescription>
              Send <code>push</code>, <code>workflow_run</code>, or{" "}
              <code>check_suite</code> events to ThreatLens.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
              <Input
                readOnly
                value={ghUrl}
                className="bg-neutral-500 border-neutral-800"
              />
              <Button
                variant="outline"
                className="border-neutral-800 bg-neutral-500"
                onClick={() => copy(ghUrl)}
              >
                <Copy className="mr-2 h-4 w-4 " /> Copy
              </Button>
            </div>
            <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm text-neutral-300">
              <li>
                Go to{" "}
                <span className="font-medium">Repo → Settings → Webhooks</span>.
              </li>
              <li>
                Click <span className="font-medium">Add webhook</span>. Payload
                URL: <code>{ghUrl}</code>
              </li>
              <li>
                Content type: <code>application/json</code>. Secret: leave blank
                or set <code>WEBHOOK_SECRET</code> on backend.
              </li>
              <li>
                Events: <code>Send me everything</code> or pick{" "}
                <code>push</code> + <code>workflow_run</code>.
              </li>
            </ol>
          </CardContent>
        </Card>

        <Card className="mt-6 border-neutral-900 bg-neutral-950/60">
          <CardHeader>
            <CardTitle className="text-white">GitLab CI</CardTitle>
            <CardDescription>
              Alternatively, point GitLab project hooks to ThreatLens.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
              <Input
                readOnly
                value={glUrl}
                className="bg-neutral-500 border-neutral-800"
              />
              <Button
                variant="outline"
                className="border-neutral-800 bg-neutral-500"
                onClick={() => copy(glUrl)}
              >
                <Copy className="mr-2 h-4 w-4" /> Copy
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="mt-8 text-sm text-neutral-100">
          <p>Environment:</p>
          <ul className="ml-4 list-disc">
            <li>
              <code>NEXT_PUBLIC_BACKEND_URL</code> e.g.{" "}
              <code>http://localhost:8000</code> or your deployed API base URL
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
