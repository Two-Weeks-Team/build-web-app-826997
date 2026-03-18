"use client";

import type { PlanPayload } from "@/lib/api";

const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function WorkspacePanel({ plan, loading, error, busy, onRebalance, onSave }: {
  plan: PlanPayload | null;
  loading: boolean;
  error: string | null;
  busy: boolean;
  onRebalance: (fromDay: string, toDay: string) => Promise<void>;
  onSave: () => Promise<void>;
}) {
  if (loading) return <section className="rounded-lg border border-border bg-card p-4">Loading weekly meal board...</section>;
  if (error) return <section className="rounded-lg border border-destructive bg-card p-4 text-destructive">{error}</section>;
  if (!plan) return <section className="rounded-lg border border-border bg-card p-4">No plan yet. Try a seeded prompt.</section>;

  return (
    <section className="rounded-lg border border-border bg-card p-4 shadow-soft">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl">Weekly Meal Board</h2>
        <button onClick={() => void onSave()} disabled={busy} className="rounded-md border border-border bg-accent px-3 py-1 text-accent-foreground">{busy ? "Saving..." : "Save Prep Batch"}</button>
      </div>
      <div className="mt-2 text-xs text-muted-foreground">{plan.low_confidence ? "Low-confidence draft with assumptions highlighted" : "High-confidence structured draft"}</div>
      <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        {days.map((d) => (
          <article key={d} className="rounded-md border border-border bg-muted/50 p-3">
            <h3 className="text-lg">{d}</h3>
            {(plan.board[d] ?? []).map((m) => (
              <div key={m.meal} className="mt-2 rounded-md border border-border bg-card p-2">
                <p className="text-sm font-semibold">{m.meal}</p>
                <p className="text-xs text-muted-foreground">{m.portions} portions • {m.prep_effort} • leftovers: {m.leftovers}</p>
                <button onClick={() => void onRebalance(d, d === "Sun" ? "Mon" : "Sun")} className="mt-2 rounded bg-primary px-2 py-1 text-xs text-primary-foreground">Move + Rebalance</button>
              </div>
            ))}
          </article>
        ))}
      </div>
    </section>
  );
}
