"use client";

import { useState } from "react";
import type { DemoPayload } from "@/lib/api";

export default function Hero({
  demo,
  onBuild,
  busy,
  status
}: {
  demo: DemoPayload | null;
  onBuild: (query: string, preferences: string) => Promise<void>;
  busy: boolean;
  status: "loading" | "error" | "empty" | "success";
}) {
  const [query, setQuery] = useState("high protein, cheap, 3 work lunches, no peanuts");
  const [preferences, setPreferences] = useState("2 adults, one Sunday prep session, under $120");

  return (
    <section className="bench-grid rounded-lg border border-border bg-card/90 p-4 shadow-tray">
      <h1 className="text-3xl text-foreground">Meal Prep Bench</h1>
      <p className="mt-1 text-sm text-muted-foreground">From messy note to plated weekly scaffold in one pass.</p>
      <div className="mt-4 space-y-3">
        <textarea value={query} onChange={(e) => setQuery(e.target.value)} className="min-h-24 w-full rounded-md border border-border bg-muted p-2 text-sm" />
        <textarea value={preferences} onChange={(e) => setPreferences(e.target.value)} className="min-h-20 w-full rounded-md border border-border bg-muted p-2 text-sm" />
        <button
          onClick={() => void onBuild(query, preferences)}
          disabled={busy}
          className="w-full rounded-md bg-primary px-4 py-2 text-primary-foreground disabled:opacity-60"
        >
          {busy ? "Building..." : "Build My Meal Plan"}
        </button>
      </div>
      <div className="mt-4">
        <p className="text-xs uppercase tracking-wide text-muted-foreground">Example prompts</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {(demo?.seeds ?? []).map((seed) => (
            <button key={seed} onClick={() => setQuery(seed)} className="rounded-full border border-border bg-muted px-3 py-1 text-xs">
              {seed}
            </button>
          ))}
        </div>
      </div>
      <p className="mt-3 text-xs text-warning">Status: {status}. Draft mode keeps moving even with missing details.</p>
    </section>
  );
}
