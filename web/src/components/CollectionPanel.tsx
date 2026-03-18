"use client";

import type { DemoPayload, PlanPayload } from "@/lib/api";

export default function CollectionPanel({ demo, activePlan }: { demo: DemoPayload | null; activePlan: PlanPayload | null }) {
  return (
    <section className="rounded-lg border border-border bg-card p-4">
      <h3 className="text-xl">Saved Prep Batch Pantry Shelf</h3>
      <div className="mt-3 space-y-2">
        {(demo?.saved_runs ?? []).map((run) => (
          <div key={run.id} className="rounded-md border border-border bg-muted/40 p-2 text-sm">
            <div className="flex items-center justify-between">
              <span>{run.name}</span>
              <span className="text-xs text-muted-foreground">{run.timestamp}</span>
            </div>
            {run.low_confidence ? <p className="mt-1 text-xs text-warning">Assumption-aware draft</p> : <p className="mt-1 text-xs text-success">Ready to reuse</p>}
          </div>
        ))}
      </div>
      {activePlan?.assumptions?.length ? (
        <div className="mt-3 rounded-md border border-warning/40 bg-muted p-2">
          <p className="text-xs uppercase text-warning">Assumption callouts</p>
          <ul className="mt-1 list-disc pl-4 text-xs text-muted-foreground">
            {activePlan.assumptions.map((a) => <li key={a}>{a}</li>)}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
