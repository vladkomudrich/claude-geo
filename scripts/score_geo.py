#!/usr/bin/env python3
"""
score_geo.py — Aggregate pillar scores into a single GEO Score.

Usage:
    python score_geo.py --input audit-data.json
    python score_geo.py --input audit-data.json --output scored.json

Expects input JSON with five pillar scores (0-100 each):
  {
    "brand": "Acme",
    "url": "https://acme.com",
    "pillars": {
      "technical": {"score": 75, "findings": [...]},
      "content": {"score": 60, "findings": [...]},
      "schema": {"score": 50, "findings": [...]},
      "presence": {"score": 40, "findings": [...]},
      "mentions": {"score": 30, "findings": [...]}
    },
    "critical_failures": [...],
    "actions": [{"action": "...", "pillar": "...", "score_delta": 15, "effort_hours": 2}, ...]
  }

Outputs total weighted score, grade A-F, and ranks top-5 actions by leverage.
"""
import argparse
import json
import sys


WEIGHTS = {
    "technical": 0.20,
    "content": 0.25,
    "schema": 0.15,
    "presence": 0.25,
    "mentions": 0.15,
}


def grade(total: float) -> str:
    if total >= 85:
        return "A"
    if total >= 70:
        return "B"
    if total >= 55:
        return "C"
    if total >= 40:
        return "D"
    return "F"


def grade_meaning(g: str) -> str:
    return {
        "A": "Excellent GEO posture — maintain and monitor.",
        "B": "Strong but with specific gaps — see top 5 actions.",
        "C": "Average — measurable upside in 60-90 days.",
        "D": "Significant gaps — prioritize critical findings.",
        "F": "Critical — site is largely invisible to AI engines.",
    }[g]


def tier_action(effort_hours: float) -> str:
    """Tier actions by effort. Quick win ≤ 2h, medium 2-16h, high impact > 16h."""
    if effort_hours <= 2:
        return "quick_wins"
    if effort_hours <= 16:
        return "medium_effort"
    return "high_impact"


def project_platforms(pillars: dict) -> dict:
    """Estimate per-platform impact given the five pillar scores.

    Each AI engine weighs the pillars differently. Multipliers tuned from the
    `platforms-2026.md` reference. Result is a 0-100 projected visibility score
    per engine — useful for prioritizing actions.
    """
    weights = {
        # Each engine gets a different mix:
        "google_aio":  {"technical": 0.25, "content": 0.20, "schema": 0.30, "presence": 0.15, "mentions": 0.10},
        "chatgpt":     {"technical": 0.15, "content": 0.20, "schema": 0.15, "presence": 0.30, "mentions": 0.20},
        "perplexity":  {"technical": 0.15, "content": 0.20, "schema": 0.10, "presence": 0.35, "mentions": 0.20},
        "claude":      {"technical": 0.20, "content": 0.30, "schema": 0.15, "presence": 0.15, "mentions": 0.20},
        "copilot":     {"technical": 0.25, "content": 0.20, "schema": 0.30, "presence": 0.15, "mentions": 0.10},
    }
    notes = {
        "google_aio": "Weights: schema-heavy + technical + content.",
        "chatgpt": "Weights: own product page + G2 ≥4.0 + Wikipedia presence.",
        "perplexity": "Weights: Reddit + YouTube + freshness.",
        "claude": "Weights: first-party docs + primary-source citations.",
        "copilot": "Weights: Bing index + structured data + LinkedIn.",
    }
    out = {}
    for engine, w in weights.items():
        score = sum(pillars.get(p, {}).get("score", 0) * mult for p, mult in w.items())
        out[engine] = {
            "projected_score": round(score, 1),
            "note": notes[engine],
        }
    return out


def compute(payload: dict) -> dict:
    pillars = payload.get("pillars", {})
    weighted_total = 0.0
    pillar_details = {}
    for name, weight in WEIGHTS.items():
        info = pillars.get(name, {})
        score = float(info.get("score", 0))
        weighted = score * weight
        weighted_total += weighted
        pillar_details[name] = {
            "score": score,
            "weight": weight,
            "weighted_contribution": round(weighted, 2),
            "findings": info.get("findings", []),
        }

    total = round(weighted_total, 1)
    g = grade(total)

    # Rank actions by leverage = score_delta / effort_hours, then tier them.
    actions = payload.get("actions", [])
    for a in actions:
        e = max(0.5, float(a.get("effort_hours", 1)))
        a["leverage"] = round(float(a.get("score_delta", 0)) / e, 2)
        a["tier"] = tier_action(float(a.get("effort_hours", 1)))
    actions_sorted = sorted(actions, key=lambda a: -a["leverage"])

    tiered = {"quick_wins": [], "medium_effort": [], "high_impact": []}
    for a in actions_sorted:
        tier = a.get("tier", "medium_effort")
        tiered[tier].append(a)

    return {
        "brand": payload.get("brand"),
        "url": payload.get("url"),
        "narrative_thesis": payload.get("narrative_thesis", ""),
        "whats_working": payload.get("whats_working", []),
        "total_score": total,
        "grade": g,
        "grade_meaning": grade_meaning(g),
        "pillars": pillar_details,
        "platform_projections": project_platforms(pillar_details),
        "critical_failures": payload.get("critical_failures", []),
        "top_5_actions": actions_sorted[:5],  # kept for backward compat
        "tiered_actions": tiered,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        payload = json.load(f)
    scored = compute(payload)
    if args.output:
        with open(args.output, "w") as f:
            json.dump(scored, f, indent=2)
        print(f"Wrote {args.output}")
    else:
        print(json.dumps(scored, indent=2))


if __name__ == "__main__":
    main()
