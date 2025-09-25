'use client';

import { useSearchParams } from 'next/navigation';
import { useMemo } from 'react';

export default function NewScanClient() {
  const searchParams = useSearchParams();

  // Example usage
  const repo = useMemo(() => searchParams.get('repo') ?? '', [searchParams]);

  return (
    <div className="p-6">
      {/* Your real UI here */}
      <h1 className="text-xl font-semibold">New Scan</h1>
      <p className="mt-2">Repo: {repo || '—'}</p>
    </div>
  );
}
