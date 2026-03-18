"use client";

import { FormEvent, useEffect, useState } from "react";
import { createPlan, fetchInsights, fetchItems, InsightsResponse, PlanResponse } from "@/lib/api";
import FeaturePanel from "@/components/FeaturePanel";
import StatePanel from "@/components/StatePanel";
import StatsStrip from "@/components/StatsStrip";
import ReferenceShelf from "@/components/ReferenceShelf";

export default function Page() {
  const [query, setQuery] = useState("high protein, cheap, 3 work lunches, no peanuts");
  const [preferences, setPreferences] = useState("high-protein,budget,3-lunches,no-peanuts");
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [insights, setInsights] = useState<InsightsResponse | null>(null);
  const [state, setState] = useState<"loading" | "empty" | "error" | "success">("loading");
  const [message, setMessage] = useState("Heating up the prep bench...");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const initial = await fetchItems();
        setPlan(initial);
        const i = await fetchInsights({ selection: initial.items[0] || "Weekly Meal Plan", context: initial.summary });
        setInsights(i);
        setState("success");
        setMessage("First-pass weekly scaffold loaded.");
      } catch (e) {
        setState("error");
        setMessage(e instanceof Error ? e.message : "Failed to load starter artifacts.");
      }
    })();
  }, []);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setState("loading");
    setMessage("Plating your weekly board in one pass...");
    try {
      const next = await createPlan({ query, preferences: preferences.split(",").map((p) => p.trim()).filter(Boolean) });
      setPlan(next);
      const i = await fetchInsights({ selection: next.items[0] || "Grocery List", context: next.summary });
      setInsights(i);
      setState("success");
      setMessage("Meal board, grocery basket, and prep notes refreshed with live assumptions.");
    } catch (e) {
      setState("error");
      setMessage(e instanceof Error ? e.message : "Could not build plan");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen p-4 md:p-6">
      <div className="mx-auto max-w-[1400px] space-y-4">
        <header className="rounded-lg border border-border bg-card p-5 shadow-soft">
          <h1 className="font-[--font-display] text-4xl md:text-5xl">Prep Bench Studio</h1>
          <p className="mt-2 text-muted-foreground">Turn rough meal-prep intent into a plated weekly plan, grocery list, and prep batch artifacts.</p>
        </header>

        <StatsStrip score={plan?.score ?? 0} meals={plan?.items.length ?? 0} />
        <StatePanel state={state} message={message} />

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
          <section className="lg:col-span-3 space-y-4 rounded-lg border border-border bg-card p-4">
            <h2 className="font-[--font-display] text-2xl">Intake Tray</h2>
            <form onSubmit={onSubmit} className="space-y-3">
              <label className="text-sm text-muted-foreground">What kind of meal prep week do you want?</label>
              <textarea value={query} onChange={(e) => setQuery(e.target.value)} className="w-full rounded-md border border-border bg-muted p-3 text-foreground" rows={4} />
              <label className="text-sm text-muted-foreground">Diet, budget, servings, schedule, and ingredient constraints</label>
              <input value={preferences} onChange={(e) => setPreferences(e.target.value)} className="w-full rounded-md border border-border bg-muted p-2" />
              <button disabled={busy} type="submit" onClick={() => {}} className="w-full rounded-md bg-primary px-4 py-2 text-primary-foreground disabled:opacity-60">
                {busy ? "Building..." : "Build My Meal Plan"}
              </button>
            </form>
            <ReferenceShelf onPick={(seed) => setQuery(seed)} />
          </section>

          <section className="lg:col-span-6 rounded-lg border border-border bg-card p-4">
            <h2 className="font-[--font-display] text-2xl">Weekly Meal Board</h2>
            {!plan?.items?.length ? (
              <p className="mt-3 text-muted-foreground">No meals scaffolded yet.</p>
            ) : (
              <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-2">
                {plan.items.map((item, idx) => (
                  <button key={idx} onClick={async () => setInsights(await fetchInsights({ selection: item, context: plan.summary }))} className="rounded-lg border border-border bg-muted p-3 text-left shadow-pin transition-transform hover:-translate-y-0.5">
                    <p className="font-medium">{item}</p>
                    <p className="text-xs text-muted-foreground">Pinned card • tap to rebalance insights</p>
                  </button>
                ))}
              </div>
            )}
          </section>

          <section className="lg:col-span-3 space-y-4 rounded-lg border border-border bg-card p-4">
            <h2 className="font-[--font-display] text-2xl">Prep Artifact Rail</h2>
            <FeaturePanel assumptions={insights?.highlights ?? ["Assuming one shared grocery run on Sunday", "Assuming 30-minute weekday prep windows"]} />
            <div className="rounded-lg border border-border bg-muted p-3">
              <h3 className="font-[--font-display] text-xl">Grocery Basket + Prep Notes</h3>
              <ul className="mt-2 list-disc pl-5 text-sm text-muted-foreground">
                {(insights?.insights ?? ["Batch-cook grains once", "Double broccoli for lunch leftovers", "Use yogurt cups as snack anchors"]).map((x, i) => <li key={i}>{x}</li>)}
              </ul>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
