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

    # Rank actions by leverage = score_delta / effort_hours
    actions = payload.get("actions", [])
    for a in actions:
        e = max(0.5, float(a.get("effort_hours", 1)))
        a["leverage"] = round(float(a.get("score_delta", 0)) / e, 2)
    top_actions = sorted(actions, key=lambda a: -a["leverage"])[:5]

    return {
        "brand": payload.get("brand"),
        "url": payload.get("url"),
        "total_score": total,
        "grade": g,
        "grade_meaning": grade_meaning(g),
        "pillars": pillar_details,
        "critical_failures": payload.get("critical_failures", []),
        "top_5_actions": top_actions,
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
