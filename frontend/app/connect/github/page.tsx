import React from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Github, ShieldCheck } from "lucide-react";

export default function ConnectGitHubPage() {
  const installUrl =
    process.env.NEXT_PUBLIC_GITHUB_APP_INSTALL_URL ||
    process.env.NEXT_PUBLIC_GITHUB_OAUTH_URL ||
    "https://github.com/apps/YOUR-GITHUB-APP/installations/new";

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <div className="mx-auto max-w-3xl px-4 py-10">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-fuchsia-600 via-purple-600 to-cyan-500">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <h1 className="text-2xl font-bold">Connect GitHub</h1>
        </div>

        <Card className="border-neutral-900 bg-neutral-950/60">
          <CardHeader>
            <CardTitle>Authorize ThreatLens</CardTitle>
            <CardDescription>
              Grant minimal read access to repositories so ThreatLens can
              monitor CI/CD events.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button
                asChild
                className="bg-gradient-to-tr from-fuchsia-600 to-purple-600 hover:from-fuchsia-500 hover:to-purple-500"
              >
                <a href={installUrl} target="_blank" rel="noreferrer">
                  <Github className="mr-2 h-4 w-4" /> Continue with GitHub
                </a>
              </Button>
              <Button
                variant="outline"
                asChild
                className="border-neutral-800 bg-neutral-950"
              >
                <a
                  href="https://docs.github.com/en/apps"
                  target="_blank"
                  rel="noreferrer"
                >
                  GitHub App guide
                </a>
              </Button>
            </div>
            <p className="mt-4 text-sm text-neutral-300">
              Tip: Prefer a <span className="font-medium">GitHub App</span> over
              personal tokens. Apps scope perms narrowly and are easier to
              revoke.
            </p>
          </CardContent>
        </Card>

        <div className="mt-8 text-sm text-neutral-400">
          <p>Environment:</p>
          <ul className="ml-4 list-disc">
            <li>
              <code>NEXT_PUBLIC_GITHUB_APP_INSTALL_URL</code> (recommended)
            </li>
            <li>
              <code>NEXT_PUBLIC_GITHUB_OAUTH_URL</code> (fallback)
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
