import json
import os
import re
from typing import Any

import httpx


DO_INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"
DEFAULT_MODEL = os.getenv("DO_INFERENCE_MODEL", "anthropic-claude-4.6-sonnet")


def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def _coerce_unstructured_payload(raw_text: str) -> dict[str, object]:
    compact = raw_text.strip()
    normalized = compact.replace("\n", ",")
    tags = [part.strip(" -•\t") for part in normalized.split(",") if part.strip(" -•\t")]
    if not tags:
        tags = ["guided plan", "saved output", "shareable insight"]
    headline = tags[0].title()
    items = []
    for index, tag in enumerate(tags[:3], start=1):
        items.append({
            "title": f"Stage {index}: {tag.title()}",
            "detail": f"Use {tag} to move the request toward a demo-ready outcome.",
            "score": min(96, 80 + index * 4),
        })
    highlights = [tag.title() for tag in tags[:3]]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact or f"{headline} fallback is ready for review.",
        "tags": tags[:6],
        "items": items,
        "score": 88,
        "insights": [f"Lead with {headline} on the first screen.", "Keep one clear action visible throughout the flow."],
        "next_actions": ["Review the generated plan.", "Save the strongest output for the demo finale."],
        "highlights": highlights,
    }

def _normalize_inference_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return _coerce_unstructured_payload(str(payload))
    normalized = dict(payload)
    summary = str(normalized.get("summary") or normalized.get("note") or "AI-generated plan ready")
    raw_items = normalized.get("items")
    items: list[dict[str, object]] = []
    if isinstance(raw_items, list):
        for index, entry in enumerate(raw_items[:3], start=1):
            if isinstance(entry, dict):
                title = str(entry.get("title") or f"Stage {index}")
                detail = str(entry.get("detail") or entry.get("description") or title)
                score = float(entry.get("score") or min(96, 80 + index * 4))
            else:
                label = str(entry).strip() or f"Stage {index}"
                title = f"Stage {index}: {label.title()}"
                detail = f"Use {label} to move the request toward a demo-ready outcome."
                score = float(min(96, 80 + index * 4))
            items.append({"title": title, "detail": detail, "score": score})
    if not items:
        items = _coerce_unstructured_payload(summary).get("items", [])
    raw_insights = normalized.get("insights")
    if isinstance(raw_insights, list):
        insights = [str(entry) for entry in raw_insights if str(entry).strip()]
    elif isinstance(raw_insights, str) and raw_insights.strip():
        insights = [raw_insights.strip()]
    else:
        insights = []
    next_actions = normalized.get("next_actions")
    if isinstance(next_actions, list):
        next_actions = [str(entry) for entry in next_actions if str(entry).strip()]
    else:
        next_actions = []
    highlights = normalized.get("highlights")
    if isinstance(highlights, list):
        highlights = [str(entry) for entry in highlights if str(entry).strip()]
    else:
        highlights = []
    if not insights and not next_actions and not highlights:
        fallback = _coerce_unstructured_payload(summary)
        insights = fallback.get("insights", [])
        next_actions = fallback.get("next_actions", [])
        highlights = fallback.get("highlights", [])
    return {
        **normalized,
        "summary": summary,
        "items": items,
        "score": float(normalized.get("score") or 88),
        "insights": insights,
        "next_actions": next_actions,
        "highlights": highlights,
    }


async def _call_inference(messages: list[dict[str, str]], max_tokens: int = 512) -> dict[str, Any]:
    key = os.getenv("GRADIENT_MODEL_ACCESS_KEY") or os.getenv("DIGITALOCEAN_INFERENCE_KEY")
    if not key:
        return {
            "note": "AI temporarily unavailable: missing GRADIENT_MODEL_ACCESS_KEY or DIGITALOCEAN_INFERENCE_KEY.",
            "fallback": True,
        }

    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_completion_tokens": max(256, max_tokens),
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(DO_INFERENCE_URL, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
            content = (
                body.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "{}")
            )
            clean = _extract_json(content)
            return json.loads(clean)
    except Exception as exc:
        return {
            "note": f"AI temporarily unavailable; using deterministic fallback. ({str(exc)})",
            "fallback": True,
        }


async def parse_messy_prompt(query: str, preferences: str) -> dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": "You are a meal-prep planning parser. Return strict JSON with keys: goals (list), servings (int), budget (string), schedule (string), dietary_constraints (list), assumptions (list), confidence (string: high|medium|low).",
        },
        {
            "role": "user",
            "content": f"Query: {query}\nPreferences: {preferences}",
        },
    ]
    return await _call_inference(messages, max_tokens=512)


async def generate_plan_artifacts(structured_brief: dict[str, Any]) -> dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": "Return strict JSON with keys: summary (string), items (array of 7 day objects with breakfast/lunch/dinner), score (number 0-100), grocery_list (array of {item, quantity}), prep_batch (array of step strings), meal_prep_notes (array of strings), assumptions (array), confidence (high|medium|low). Keep practical and budget-aware.",
        },
        {"role": "user", "content": json.dumps(structured_brief, ensure_ascii=False)},
    ]
    return await _call_inference(messages, max_tokens=512)


async def generate_insights(selection: str, context: str) -> dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": "Return strict JSON with keys: insights (array of strings), next_actions (array of strings), highlights (array of strings). Domain: meal-prep optimization with leftovers, grocery efficiency, and prep timing.",
        },
        {"role": "user", "content": f"Selection: {selection}\nContext: {context}"},
    ]
    return await _call_inference(messages, max_tokens=512)
