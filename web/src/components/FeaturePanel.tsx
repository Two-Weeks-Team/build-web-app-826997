"use client";

export default function FeaturePanel({ assumptions }: { assumptions: string[] }) {
  return (
    <section className="rounded-lg border border-border bg-card p-4 shadow-soft">
      <h3 className="font-[--font-display] text-2xl">Structured Brief & Assumptions</h3>
      <div className="mt-3 grid gap-2 text-sm text-muted-foreground">
        {assumptions.map((a, i) => (
          <p key={i} className="rounded-md border border-warning/40 bg-muted px-3 py-2 text-warning">✍️ {a}</p>
        ))}
      </div>
    </section>
  );
}
