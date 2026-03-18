"use client";

import type { PlanPayload } from "@/lib/api";

export default function InsightPanel({ plan, onRefresh, busy }: { plan: PlanPayload | null; onRefresh: () => Promise<void>; busy: boolean }) {
  return (
    <section className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl">Prep Artifact Rail</h3>
        <button onClick={() => void onRefresh()} disabled={busy} className="rounded-md border border-border px-2 py-1 text-xs">{busy ? "Refreshing" : "Refresh Insights"}</button>
      </div>
      <div className="mt-3 space-y-3">
        <div>
          <p className="text-xs uppercase text-muted-foreground">Grocery Basket</p>
          <ul className="mt-1 space-y-1 text-sm">
            {(plan?.grocery ?? []).slice(0, 6).map((g) => <li key={g.item}>{g.item} — {g.qty}</li>)}
          </ul>
        </div>
        <div>
          <p className="text-xs uppercase text-muted-foreground">Prep Notes</p>
          <ul className="mt-1 list-disc pl-4 text-sm">
            {(plan?.prep_notes ?? []).slice(0, 4).map((n) => <li key={n}>{n}</li>)}
          </ul>
        </div>
      </div>
    </section>
  );
}
