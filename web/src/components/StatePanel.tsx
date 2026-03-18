"use client";

type Props = { state: "loading" | "empty" | "error" | "success"; message: string };

export default function StatePanel({ state, message }: Props) {
  const color = state === "error" ? "text-destructive" : state === "loading" ? "text-warning" : state === "success" ? "text-success" : "text-muted-foreground";
  return <div className={`rounded-md border border-border bg-muted px-3 py-2 text-sm ${color}`}>{message}</div>;
}
