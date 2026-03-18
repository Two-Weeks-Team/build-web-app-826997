"use client";

export default function StatsStrip({ score, meals }: { score: number; meals: number }) {
  return (
    <div className="grid grid-cols-3 gap-2">
      <div className="rounded-md border border-border bg-card p-3"><p className="text-xs text-muted-foreground">Draft confidence</p><p className="text-xl text-success">{score}%</p></div>
      <div className="rounded-md border border-border bg-card p-3"><p className="text-xs text-muted-foreground">Meals scaffolded</p><p className="text-xl">{meals}</p></div>
      <div className="rounded-md border border-border bg-card p-3"><p className="text-xs text-muted-foreground">Rebalance status</p><p className="text-xl text-warning">Live</p></div>
    </div>
  );
}
