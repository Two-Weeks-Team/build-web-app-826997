export type PlanRequest = { query: string; preferences: string[] };
export type PlanResponse = { summary: string; items: string[]; score: number };
export type InsightsRequest = { selection: string; context: string };
export type InsightsResponse = { insights: string[]; next_actions: string[]; highlights: string[] };

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || "Request failed");
  }
  return res.json() as Promise<T>;
}

export async function fetchItems(): Promise<PlanResponse> {
  const res = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: "high protein, cheap, 3 work lunches, no peanuts",
      preferences: ["high-protein", "budget", "work-lunch", "no-peanuts"]
    })
  });
  return parseJson<PlanResponse>(res);
}

export async function createPlan(payload: PlanRequest): Promise<PlanResponse> {
  const res = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return parseJson<PlanResponse>(res);
}

export async function fetchInsights(payload: InsightsRequest): Promise<InsightsResponse> {
  const res = await fetch("/api/insights", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return parseJson<InsightsResponse>(res);
}
