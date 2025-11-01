import { Suspense } from "react";
import NewScanClient from "./NewScanClient";

export const dynamic = "force-dynamic"; // avoid prerender issues during build

export default function NewScanPage() {
  return (
    <Suspense fallback={<div className="p-6 text-gray-400">Loading…</div>}>
      <NewScanClient />
    </Suspense>
  );
}
