"use client";
interface ScanResult {
  status: string;
  repo: string;
  branch?: string;
  commit?: string;
  summary?: {
    trivy?: {
      counts?: {
        targets_scanned: number;
        vulnerabilities: number;
        misconfigurations: number;
        secrets: number;
      };
    };
    gitleaks?: {
      leaks: number;
    };
  };
  llm_input?: unknown;
  trivy?: {
    returncode: number;
    stderr?: string;
    json?: unknown;
  };
  gitleaks?: {
    returncode: number;
    stderr?: string;
    json?: unknown;
  };
}

import { useSearchParams } from "next/navigation";
import { useState, useMemo } from "react";
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

export default function NewScanClient() {
  const searchParams = useSearchParams();
  const initialRepo = useMemo(
    () => searchParams.get("repo") ?? "",
    [searchParams]
  );
  const [repoUrl, setRepoUrl] = useState(initialRepo);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleScan() {
    if (!repoUrl.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Scan failed");
      setResult(data);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError("An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto mt-16">
      <Card className="shadow-lg border-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="text-green-500" />
            New Repository Scan
          </CardTitle>
          <CardDescription>
            Enter a GitHub repository URL to scan for secrets, vulnerabilities,
            and misconfigurations.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="repo">Repository URL</Label>
            <Input
              id="repo"
              type="text"
              placeholder="https://github.com/your/repo"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              className="text-sm"
            />
          </div>

          <Button
            onClick={handleScan}
            disabled={loading}
            className="w-full mt-3"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin mr-2 h-4 w-4" /> Scanning…
              </>
            ) : (
              <>
                Start Scan <ChevronRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>

          {error && (
            <p className="text-sm text-red-400 border-t pt-3">⚠️ {error}</p>
          )}

          {result && (
            <pre className="bg-gray-900 text-green-400 p-4 mt-4 rounded-lg overflow-x-auto text-xs">
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
