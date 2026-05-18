#!/usr/bin/env python3
"""
check_schema.py — Extract and validate JSON-LD schema for GEO priorities.

Usage:
    python check_schema.py <url>
        [--type=Organization]
        [--property=knowsAbout|sameAs]
        [--chain]
        [--json]

GEO priorities (May 2026):
  - Organization with knowsAbout (>=3 topics)
  - Organization with sameAs (>=4 platform URLs)
  - Product / SoftwareApplication / Service linked to Organization
  - FAQPage (for AI extraction; note Google rich results deprecated 7 May 2026)
  - Person schema with sameAs
  - Entity chain depth: Product -> Org -> founder -> Person
  - HARD FAIL if HowTo present (deprecated Sept 2023)

Used by geo-schema sub-agent and `/geo verify schema-*` commands.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
import urllib.error
from html.parser import HTMLParser


USER_AGENT = "claude-geo/1.0 (+https://vdigital.app)"


class JsonLdExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_ld = False
        self.blocks = []
        self.current = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            for k, v in attrs:
                if k.lower() == "type" and v and v.strip().lower() == "application/ld+json":
                    self.in_ld = True
                    self.current = []
                    return

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.in_ld:
            self.blocks.append("".join(self.current))
            self.in_ld = False
            self.current = []

    def handle_data(self, data):
        if self.in_ld:
            self.current.append(data)


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            return {"url": url, "html": html}
    except urllib.error.HTTPError as e:
        return {"url": url, "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"url": url, "error": str(e)}


def parse_blocks(blocks: list[str]) -> list[dict]:
    parsed = []
    for raw in blocks:
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            parsed.append({"_error": f"Parse error: {e}", "_raw": raw[:200]})
            continue
        # @graph expansion
        if isinstance(data, dict) and "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                if isinstance(item, dict):
                    parsed.append(item)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    parsed.append(item)
        elif isinstance(data, dict):
            parsed.append(data)
    return parsed


def gather_types(items: list[dict]) -> dict:
    types = {}
    for item in items:
        t = item.get("@type")
        if isinstance(t, list):
            for ti in t:
                types.setdefault(ti, []).append(item)
        elif isinstance(t, str):
            types.setdefault(t, []).append(item)
    return types


def check_organization(items: list[dict]) -> dict:
    """Check Organization schema for knowsAbout and sameAs."""
    orgs = [i for i in items if i.get("@type") == "Organization"]
    if not orgs:
        return {"present": False}

    org = orgs[0]  # take first
    knows_about = org.get("knowsAbout") or []
    same_as = org.get("sameAs") or []
    if isinstance(same_as, str):
        same_as = [same_as]
    if isinstance(knows_about, str):
        knows_about = [knows_about]

    return {
        "present": True,
        "name": org.get("name"),
        "knowsAbout_count": len(knows_about),
        "knowsAbout": knows_about[:10],
        "sameAs_count": len(same_as),
        "sameAs": same_as,
        "founder_present": "founder" in org,
    }


def check_entity_chain(items: list[dict]) -> dict:
    """Check whether Product/Service/SoftwareApplication links back to Organization."""
    products = [i for i in items if i.get("@type") in {"Product", "SoftwareApplication", "Service", "WebApplication"}]
    if not products:
        return {"present": False, "reason": "No Product/SoftwareApplication/Service found."}

    chain = []
    for p in products:
        for key in ("manufacturer", "provider", "publisher", "brand"):
            if key in p:
                chain.append(f"{p.get('@type')}.{key} -> {p[key].get('@type') if isinstance(p[key], dict) else type(p[key]).__name__}")
                break
    return {"present": bool(chain), "links": chain, "products_count": len(products)}


def score(report: dict) -> int:
    s = 0
    types = report["types_found"]
    org = report["organization"]
    if "Organization" in types:
        s += 15
    if org.get("present") and org.get("knowsAbout_count", 0) >= 3:
        s += 15
    if org.get("present") and org.get("sameAs_count", 0) >= 3:
        s += 15
    if any(t in types for t in {"Product", "SoftwareApplication", "Service"}):
        s += 10
    if "FAQPage" in types:
        s += 10
    if "Person" in types:
        s += 5
    if "BreadcrumbList" in types:
        s += 5
    if len([t for t in types if t in {"Organization", "WebSite", "Product", "SoftwareApplication", "Article", "BlogPosting", "FAQPage", "Person", "BreadcrumbList", "Service"}]) >= 3:
        s += 10
    if "WebSite" in types and any("SearchAction" in str(i) for i in report["items"]):
        s += 5
    if report["entity_chain"].get("present"):
        s += 10
    # Apply HowTo auto-cap AFTER scoring (deprecated Sept 2023 — sites using
    # it can never exceed 30 on this pillar regardless of other strengths).
    if "HowTo" in types:
        return min(s, 30)
    return min(s, 100)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--type", help="Check for a specific @type")
    parser.add_argument("--property", help="Check a specific property on Organization (knowsAbout / sameAs)")
    parser.add_argument("--chain", action="store_true", help="Check entity chain")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    fetched = fetch(args.url)
    if "error" in fetched:
        out = {"url": args.url, "error": fetched["error"], "score": 0}
        print(json.dumps(out, indent=2) if args.json else f"ERROR: {fetched['error']}")
        sys.exit(2)

    extractor = JsonLdExtractor()
    extractor.feed(fetched["html"])
    items = parse_blocks(extractor.blocks)
    types_found = list(gather_types(items).keys())

    report = {
        "url": args.url,
        "json_ld_blocks": len(extractor.blocks),
        "items": items,
        "types_found": types_found,
        "organization": check_organization(items),
        "entity_chain": check_entity_chain(items),
        "deprecated_in_use": [t for t in types_found if t in {"HowTo", "SpecialAnnouncement"}],
    }
    report["score"] = score(report)

    # Filter by --type/--property if specified
    if args.type:
        present = args.type in types_found
        report["target_type_present"] = present

    if args.property:
        if args.property == "knowsAbout":
            report["target_property"] = {
                "present": report["organization"].get("knowsAbout_count", 0) > 0,
                "count": report["organization"].get("knowsAbout_count", 0),
                "values": report["organization"].get("knowsAbout", []),
            }
        elif args.property == "sameAs":
            report["target_property"] = {
                "present": report["organization"].get("sameAs_count", 0) > 0,
                "count": report["organization"].get("sameAs_count", 0),
                "values": report["organization"].get("sameAs", []),
            }

    if args.json:
        # Slim payload — drop full items[] (can be many KB of nested JSON-LD).
        # Keep a compact summary so callers know what was parsed.
        items_summary = []
        for it in items[:20]:  # cap at 20
            if not isinstance(it, dict):
                continue
            t = it.get("@type")
            if isinstance(t, list):
                t = t[0] if t else None
            items_summary.append({
                "@type": t,
                "name": it.get("name"),
                "has_url": "url" in it,
            })
        report_out = {k: v for k, v in report.items() if k != "items"}
        report_out["items_summary"] = items_summary
        report_out["items_total"] = len(items)
        print(json.dumps(report_out, indent=2, default=str))
    else:
        print(f"Schema check for {args.url}")
        print(f"JSON-LD blocks: {report['json_ld_blocks']}")
        print(f"Pillar 3 score: {report['score']}/100")
        print(f"@types found: {', '.join(types_found) if types_found else '(none)'}")
        org = report["organization"]
        if org.get("present"):
            print(f"\nOrganization: {org.get('name','?')}")
            print(f"  knowsAbout: {org['knowsAbout_count']} topics")
            print(f"  sameAs: {org['sameAs_count']} links")
        else:
            print("\nOrganization: NOT FOUND — highest-priority addition.")
        chain = report["entity_chain"]
        print(f"\nEntity chain: {'YES' if chain.get('present') else 'NO'}")
        if chain.get("present"):
            for link in chain.get("links", []):
                print(f"  {link}")
        if report["deprecated_in_use"]:
            print(f"\n⚠ DEPRECATED types in use: {', '.join(report['deprecated_in_use'])}")
            print("  HowTo: rich results retired Sept 2023. Auto-caps Pillar 3 at 30.")


if __name__ == "__main__":
    main()
