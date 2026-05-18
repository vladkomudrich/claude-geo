#!/usr/bin/env python3
"""
check_wikipedia.py — Check for Wikipedia and Wikidata presence for a brand.

Usage:
    python check_wikipedia.py "<brand name>" [--json]

Uses the Wikipedia REST API (public, no key needed) and Wikidata API.

Used by geo-trust and geo-presence sub-agents.
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
import urllib.error


USER_AGENT = "claude-geo/1.0 (+https://vdigital.app)"


def http_get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"_error": str(e)}


def check_wikipedia(brand: str) -> dict:
    """Search English Wikipedia for the brand."""
    api = "https://en.wikipedia.org/w/api.php"
    params = urllib.parse.urlencode({
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": brand,
        "srlimit": 5,
    })
    data = http_get_json(f"{api}?{params}")
    if "_error" in data:
        return {"present": False, "error": data["_error"]}
    results = data.get("query", {}).get("search", [])
    if not results:
        return {"present": False, "search_results": []}

    # Take top result and check it's a close title match
    top = results[0]
    title_match = brand.lower() in top["title"].lower() or top["title"].lower() in brand.lower()

    # Fetch summary for top match
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(top['title'])}"
    summary = http_get_json(summary_url)

    return {
        "present": title_match,
        "search_top_title": top["title"],
        "search_top_snippet": top.get("snippet", ""),
        "page_url": summary.get("content_urls", {}).get("desktop", {}).get("page") if "_error" not in summary else None,
        "extract": summary.get("extract") if "_error" not in summary else None,
        "all_search_results": [{"title": r["title"], "snippet": r.get("snippet", "")[:200]} for r in results[:5]],
    }


def check_wikidata(brand: str) -> dict:
    """Search Wikidata for the brand."""
    api = "https://www.wikidata.org/w/api.php"
    params = urllib.parse.urlencode({
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": brand,
        "limit": 5,
    })
    data = http_get_json(f"{api}?{params}")
    if "_error" in data:
        return {"present": False, "error": data["_error"]}
    results = data.get("search", [])
    if not results:
        return {"present": False}

    top = results[0]
    # Heuristic match
    title_match = brand.lower() in top.get("label", "").lower() or top.get("label", "").lower() in brand.lower()

    return {
        "present": title_match,
        "q_id": top.get("id"),
        "label": top.get("label"),
        "description": top.get("description"),
        "concept_uri": f"https://www.wikidata.org/wiki/{top.get('id')}" if top.get("id") else None,
        "all_results": [{"id": r.get("id"), "label": r.get("label"), "description": r.get("description")} for r in results[:5]],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("brand")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    wikipedia = check_wikipedia(args.brand)
    wikidata = check_wikidata(args.brand)

    score = 0
    if wikipedia.get("present"):
        score += 20
    if wikidata.get("present"):
        score += 10

    report = {
        "brand": args.brand,
        "wikipedia": wikipedia,
        "wikidata": wikidata,
        "score_contribution": score,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Wikipedia/Wikidata for '{args.brand}'")
        print(f"Score contribution: +{score} (+20 Wikipedia, +10 Wikidata)\n")
        print("--- Wikipedia ---")
        if wikipedia.get("present"):
            print(f"✓ Article found: {wikipedia.get('search_top_title')}")
            print(f"  URL: {wikipedia.get('page_url')}")
            print(f"  Extract: {wikipedia.get('extract','')[:300]}")
        else:
            print("✗ No Wikipedia article found.")
            if wikipedia.get("all_search_results"):
                print("  Closest search hits:")
                for r in wikipedia["all_search_results"][:3]:
                    print(f"    - {r['title']}")
        print("\n--- Wikidata ---")
        if wikidata.get("present"):
            print(f"✓ Q-item: {wikidata.get('q_id')} — {wikidata.get('label')}")
            print(f"  {wikidata.get('description','')}")
            print(f"  URL: {wikidata.get('concept_uri')}")
        else:
            print("✗ No Wikidata Q-item found.")
            print("  Recommendation: Create one (~30 min). Lower bar than Wikipedia.")


if __name__ == "__main__":
    main()
