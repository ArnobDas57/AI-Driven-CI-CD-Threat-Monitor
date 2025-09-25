/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";
import { useState, Suspense } from "react";
import NewScanClient from './NewScanClient';
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ChevronRight, Loader2, ShieldCheck } from "lucide-react";

export const dynamic = 'force-dynamic';

export default function NewScanPage() {
  const params = useSearchParams();
  const initialRepo = params.get("repo") ?? "";
  const [repoUrl, setRepoUrl] = useState(initialRepo);
  const [branch, setBranch] = useState("main");
  const [commit, setCommit] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const backend =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  const runScan = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${backend}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_url: repoUrl.trim(),
          branch: branch.trim() || "main",
          ...(commit.trim() ? { commit: commit.trim() } : {}),
        }),
      });
      if (!res.ok) throw new Error(`Backend responded ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (e: any) {
      setError(e.message || "Scan failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <div className="mx-auto max-w-3xl px-4 py-10">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-fuchsia-600 via-purple-600 to-cyan-500">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <h1 className="text-2xl font-bold">New Scan</h1>
        </div>

        <Card className="border-neutral-900 bg-neutral-950/60 text-white">
          <CardHeader>
            <CardTitle>Repository</CardTitle>
            <CardDescription>
              Provide the repo info ThreatLens should analyze.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="repo">Repository URL</Label>
              <Input
                id="repo"
                placeholder="https://github.com/owner/repo"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                className="bg-neutral-900 border-neutral-800"
              />
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              <div>
                <Label htmlFor="branch">Branch</Label>
                <Input
                  id="branch"
                  placeholder="main"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  className="bg-neutral-900 border-neutral-800"
                />
              </div>
              <div>
                <Label htmlFor="commit">Commit (optional)</Label>
                <Input
                  id="commit"
                  placeholder="a1b2c3d"
                  value={commit}
                  onChange={(e) => setCommit(e.target.value)}
                  className="bg-neutral-900 border-neutral-800"
                />
              </div>
            </div>
            <Button
              onClick={runScan}
              disabled={loading || !repoUrl.trim()}
              className="bg-gradient-to-tr from-fuchsia-600 to-purple-600 hover:from-fuchsia-500 hover:to-purple-500"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Running…
                </>
              ) : (
                <>
                  Run Scan <ChevronRight className="ml-1 h-4 w-4" />
                </>
              )}
            </Button>

            {error && (
              <div className="mt-4 rounded-xl border border-red-900/60 bg-red-950/40 p-3 text-sm text-red-200">
                {error}
              </div>
            )}

            {result && (
              <div className="mt-6 space-y-3">
                <Card className="border-neutral-900 bg-neutral-900/60">
                  <CardHeader>
                    <CardTitle className="text-sm">Results</CardTitle>
                    <CardDescription>Raw response from backend</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-neutral-200">
                      {JSON.stringify(result, null, 2)}
                    </pre>
                  </CardContent>
                </Card>
                {"risk_score" in result || "summary" in result ? (
                  <Card className="border-neutral-900 bg-neutral-900/60">
                    <CardHeader>
                      <CardTitle className="text-sm">Summary</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-neutral-300">
                      {"risk_score" in result && (
                        <p>
                          <span className="font-medium">Risk:</span>{" "}
                          {String(result.risk_score)}
                        </p>
                      )}
                      {"summary" in result && (
                        <p className="mt-1">{String(result.summary)}</p>
                      )}
                    </CardContent>
                  </Card>
                ) : null}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="mt-8 text-sm text-neutral-400">
          <p>Environment:</p>
          <ul className="ml-4 list-disc">
            <li>
              <code>NEXT_PUBLIC_BACKEND_URL</code> e.g.{" "}
              <code>http://localhost:8000</code>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}


