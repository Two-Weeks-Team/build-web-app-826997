"use client";

const seeds = [
  "Protein Lunch Reset",
  "Budget Family Week",
  "Vegetarian Workweek",
  "Low-Prep High-Protein Plan",
  "Assumption-Based Draft"
];

export default function ReferenceShelf({ onPick }: { onPick: (seed: string) => void }) {
  return (
    <section className="rounded-lg border border-border bg-card p-4">
      <h3 className="font-[--font-display] text-xl">Pantry Shelf: Saved Prompt Seeds</h3>
      <div className="mt-3 flex flex-wrap gap-2">
        {seeds.map((s) => (
          <button key={s} onClick={() => onPick(s)} className="rounded-full border border-border bg-muted px-3 py-1 text-sm hover:bg-accent hover:text-accent-foreground transition-colors">
            {s}
          </button>
        ))}
      </div>
    </section>
  );
}
