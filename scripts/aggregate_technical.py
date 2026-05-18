#!/usr/bin/env python3
"""
aggregate_technical.py — Run all technical-pillar checks in ONE call.

Replaces 3-4 separate tool calls (fetch_page + check_robots_txt +
check_llms_txt + sitemap check) with a single consolidated JSON output.
Designed for the geo-technical sub-agent to reduce per-audit tool-call
count and total token usage.

Usage:
    python aggregate_technical.py <url> [--json]

Always outputs structured JSON (slim — no raw HTML, no verbose enumeration).
"""
import argparse
import json
import sys
from pathlib import Path

# Re-use the existing scripts in this same directory.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from fetch_page import fetch, check_ssr  # noqa: E402
from check_robots_txt import fetch_robots, check_bot, ALL_BOTS, RETIRED_BOTS, score_pillar  # noqa: E402
from check_llms_txt import fetch_llms_txt, validate  # noqa: E402


def slim_robots(text: str) -> dict:
    """Compact robots.txt summary: only present bots + their status, no purpose strings."""
    out = {"bots": {}, "retired_in_use": []}
    for family, bots in ALL_BOTS.items():
        # only report core families to keep payload small
        if family in {"optional"}:
            continue
        for bot_name, _ in bots:
            status = check_bot(text, bot_name)
            out["bots"][bot_name] = status
    for retired, _ in RETIRED_BOTS:
        if retired.lower() in text.lower():
            out["retired_in_use"].append(retired)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = {"url": args.url}

    # 1. Page fetch + SSR
    page = fetch(args.url)
    if "error" in page:
        report["page_fetch"] = {"error": page["error"]}
    else:
        report["page_fetch"] = {
            "status": page["status"],
            "title": page["title"],
            "body_text_length": page["body_text_length"],
            "raw_html_length": page["raw_html_length"],
            "has_cf_ray": page["has_cf_ray"],
            "ssr": check_ssr(page),
        }

    # 2. robots.txt
    robots = fetch_robots(args.url)
    if "error" in robots:
        report["robots"] = {
            "missing": robots.get("missing", False),
            "error": robots["error"],
        }
    else:
        slim = slim_robots(robots["text"])
        slim["partial_score"] = score_pillar({"bots": {b: {"status": s} for b, s in slim["bots"].items()}, "raw_text": robots["text"]})
        report["robots"] = slim

    # 3. llms.txt
    llms = fetch_llms_txt(args.url)
    if llms.get("missing"):
        report["llms_txt"] = {"status": "missing", "score": 0}
    elif "error" in llms:
        report["llms_txt"] = {"status": "error", "error": llms["error"], "score": 0}
    else:
        validation = validate(llms["text"])
        report["llms_txt"] = {
            "status": "valid" if not validation["issues"] else "malformed",
            "issues": validation["issues"],
            "section_count": validation["findings"]["section_count"],
            "link_count": validation["findings"]["link_count"],
            "score": 10 if not validation["issues"] else 5,
        }

    # 4. Compute aggregate pillar 1 score (out of 100)
    score = 0
    rb = report.get("robots", {})
    if rb.get("partial_score"):
        score += rb["partial_score"]
    # SSR contribution
    if "ssr" in report.get("page_fetch", {}):
        verdict = report["page_fetch"]["ssr"]["ssr_verdict"]
        if verdict == "ssr":
            score += 25
        elif verdict == "hybrid":
            score += 10
        elif verdict == "partial":
            score += 5
        # js-only: 0
    # llms.txt
    score += report.get("llms_txt", {}).get("score", 0)
    # Cloudflare reminder bonus
    if report.get("page_fetch", {}).get("has_cf_ray"):
        score += 5
        report["cloudflare_note"] = "cf-ray header present — verify AI Crawl Control panel in Cloudflare dashboard."

    # Critical failure detection
    critical = []
    if "ssr" in report.get("page_fetch", {}):
        if report["page_fetch"]["ssr"]["ssr_verdict"] == "js-only":
            critical.append("Site is JavaScript-only — AI crawlers see empty body. Pillar 1 capped at 40.")
            score = min(score, 40)
    if rb.get("bots"):
        all_blocked = all("disallow" in s for s in rb["bots"].values())
        if all_blocked:
            critical.append("All major AI bots disallowed in robots.txt. Pillar 1 capped at 40.")
            score = min(score, 40)

    report["pillar_1_score"] = min(score, 100)
    report["critical_failures"] = critical

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
