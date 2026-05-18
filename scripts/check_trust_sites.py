#!/usr/bin/env python3
"""
check_trust_sites.py — Check brand presence on G2, Capterra, Trustpilot,
Software Advice, GetApp, TrustRadius.

Usage:
    python check_trust_sites.py "<brand>" [--site=g2|capterra|trustpilot|all] [--json]

This uses public search (DuckDuckGo HTML) to find listings — no API keys
required. It reports the listing URL when found; deep rating extraction
requires manual verification or API integrations not bundled here.

Used by geo-trust and geo-presence sub-agents.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
import urllib.error


USER_AGENT = "Mozilla/5.0 (compatible; claude-geo/1.0; +https://vdigital.app)"

SITES = {
    "g2": "g2.com",
    "capterra": "capterra.com",
    "trustpilot": "trustpilot.com",
    "softwareadvice": "softwareadvice.com",
    "getapp": "getapp.com",
    "trustradius": "trustradius.com",
}


def ddg_search(query: str, limit: int = 5) -> list[dict]:
    """Use DuckDuckGo HTML endpoint (no API key)."""
    url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return [{"_error": str(e)}]

    # Crude regex extract — DDG HTML has stable result-link structure.
    # If DDG changes their classes the regex stops matching, returning zero
    # results indistinguishably from a genuine zero. Both old and new class
    # patterns are tried; failure surfaces as _warning.
    results = []
    patterns = [
        # Modern DDG markup
        re.compile(
            r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>.*?'
            r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
            re.DOTALL,
        ),
        # Legacy fallback — looser
        re.compile(
            r'<a[^>]+href="([^"]+)"[^>]+class="[^"]*result__a[^"]*"[^>]*>([^<]+)</a>.*?'
            r'<[^>]+class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</',
            re.DOTALL,
        ),
    ]
    pattern = next((p for p in patterns if p.search(html)), None)
    if not pattern:
        return [{"_warning": "DuckDuckGo HTML class names not matched — markup may have changed; result UNRELIABLE."}]
    for m in pattern.finditer(html):
        href = m.group(1)
        title = m.group(2)
        snippet = re.sub(r"<.*?>", "", m.group(3))
        # DDG wraps URLs in /l/?uddg=
        if "uddg=" in href:
            try:
                href = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("uddg", [href])[0]
                href = urllib.parse.unquote(href)
            except Exception:
                pass
        results.append({"url": href, "title": title.strip(), "snippet": snippet.strip()})
        if len(results) >= limit:
            break
    return results


def check_site(brand: str, site_domain: str) -> dict:
    query = f"{brand} site:{site_domain}"
    results = ddg_search(query, limit=5)
    if results and "_error" in results[0]:
        return {"present": False, "error": results[0]["_error"], "results": []}

    matching = [r for r in results if site_domain in r["url"].lower()]
    if not matching:
        return {"present": False, "results": []}

    top = matching[0]
    # Heuristic rating extraction from snippet
    rating_match = re.search(r"(\d\.\d)\s*(out of 5|/5|stars|★|rated)", top["snippet"], re.I)
    rating = float(rating_match.group(1)) if rating_match else None

    review_count_match = re.search(r"(\d[\d,]*)\s*(reviews|ratings)", top["snippet"], re.I)
    review_count = review_count_match.group(1) if review_count_match else None

    return {
        "present": True,
        "url": top["url"],
        "title": top["title"],
        "snippet": top["snippet"][:300],
        "rating_extracted": rating,
        "review_count_extracted": review_count,
        "note": "Rating from snippet — verify by visiting the page.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("brand")
    parser.add_argument("--site", default="all", choices=["all"] + list(SITES.keys()))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    sites = list(SITES.keys()) if args.site == "all" else [args.site]
    report = {"brand": args.brand, "checks": {}}
    score_contribution = 0
    critical_findings = []

    for site_key in sites:
        domain = SITES[site_key]
        result = check_site(args.brand, domain)
        report["checks"][site_key] = result
        if result.get("present"):
            rating = result.get("rating_extracted")
            if site_key == "g2":
                if rating is not None:
                    if rating >= 4.0:
                        score_contribution += 15
                    else:
                        score_contribution -= 10
                        critical_findings.append(
                            f"G2 rating {rating} < 4.0 — ChatGPT competitive-query filter applies."
                        )
                else:
                    score_contribution += 5  # listed but rating not extracted
            elif site_key == "capterra":
                if rating is not None:
                    if rating >= 4.0:
                        score_contribution += 10
                    else:
                        score_contribution -= 5
                        critical_findings.append(f"Capterra rating {rating} < 4.0.")
                else:
                    score_contribution += 5
            elif site_key == "trustpilot":
                if rating is not None and rating >= 4.0:
                    score_contribution += 10
                elif rating is not None and rating < 4.0:
                    critical_findings.append(f"Trustpilot rating {rating} < 4.0.")
                    score_contribution -= 5
                else:
                    score_contribution += 5
            else:
                score_contribution += 3

    report["score_contribution"] = score_contribution
    report["critical_findings"] = critical_findings

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Trust-site check for '{args.brand}'")
        print(f"Score contribution: {score_contribution:+}\n")
        for site_key, result in report["checks"].items():
            status = "✓" if result.get("present") else "✗"
            rating = result.get("rating_extracted")
            rating_str = f"  Rating: {rating}" if rating else "  Rating: not extracted"
            print(f"{status} {site_key:<15} {'PRESENT' if result.get('present') else 'NOT FOUND'}")
            if result.get("present"):
                print(f"  URL: {result.get('url')}")
                print(rating_str)
        if critical_findings:
            print("\n⚠ CRITICAL FINDINGS:")
            for c in critical_findings:
                print(f"  - {c}")


if __name__ == "__main__":
    main()
