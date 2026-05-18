#!/usr/bin/env python3
"""
check_llms_txt.py — Check for /llms.txt presence and structural validity.

Usage:
    python check_llms_txt.py <url> [--json]

Validates against the llms.txt standard:
  - H1 title at top
  - blockquote description
  - optional detail paragraphs
  - ## sections with markdown link lists

Used by geo-technical sub-agent and `/geo verify llms-txt`.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
import urllib.error


USER_AGENT = "claude-geo/1.0 (+https://vdigital.app)"


def fetch_llms_txt(url: str) -> dict:
    parsed = urllib.parse.urlparse(url)
    llms_url = f"{parsed.scheme}://{parsed.netloc}/llms.txt"
    req = urllib.request.Request(llms_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            return {"url": llms_url, "status": resp.status, "text": text}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"url": llms_url, "status": 404, "missing": True}
        return {"url": llms_url, "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"url": llms_url, "error": str(e)}


def validate(text: str) -> dict:
    """Structural validation of llms.txt content."""
    lines = text.strip().splitlines()
    issues = []
    findings = {
        "has_h1": False,
        "has_blockquote_description": False,
        "section_count": 0,
        "link_count": 0,
        "sections": [],
    }

    if not lines:
        issues.append("Empty file.")
        return {"issues": issues, "findings": findings}

    # H1 at top
    if lines[0].startswith("# "):
        findings["has_h1"] = True
        findings["title"] = lines[0][2:].strip()
    else:
        issues.append("First line is not an H1 (`# Title`).")

    # Blockquote
    if any(l.lstrip().startswith("> ") for l in lines[:8]):
        findings["has_blockquote_description"] = True
    else:
        issues.append("No blockquote description (`> Brief description`) near top.")

    # Sections
    current_section = None
    for line in lines:
        if line.startswith("## "):
            current_section = line[3:].strip()
            findings["section_count"] += 1
            findings["sections"].append(current_section)
        # Markdown link list items
        if re.match(r"^\s*-\s*\[.+\]\(.+\):", line):
            findings["link_count"] += 1

    if findings["section_count"] == 0:
        issues.append("No `## Section` headings found.")
    if findings["link_count"] == 0 and findings["section_count"] > 0:
        issues.append("Sections present but no markdown link items found.")

    return {"issues": issues, "findings": findings}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    fetched = fetch_llms_txt(args.url)
    report = {"url": fetched["url"]}

    if fetched.get("missing"):
        report["status"] = "missing"
        report["recommendation"] = (
            "No /llms.txt found. For developer-tool products, implement (IDE "
            "agents and MCP documentation servers actively consume it). For "
            "non-developer products, low priority — Google does not use it, "
            "and ChatGPT/Claude/Perplexity have not publicly confirmed use."
        )
        report["score"] = 0
    elif "error" in fetched:
        report["status"] = "error"
        report["error"] = fetched["error"]
        report["score"] = 0
    else:
        validation = validate(fetched["text"])
        report["status"] = "valid" if not validation["issues"] else "malformed"
        report["validation"] = validation
        report["score"] = 10 if not validation["issues"] else 5

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"llms.txt check for {report['url']}")
        print(f"Status: {report['status']}")
        print(f"Pillar 1 contribution: +{report['score']} / +10")
        if report["status"] == "missing":
            print()
            print(report["recommendation"])
        elif report["status"] == "error":
            print(f"Error: {report['error']}")
        elif report["status"] == "malformed":
            print()
            print("Issues:")
            for issue in report["validation"]["issues"]:
                print(f"  ✗ {issue}")
            print()
            print(f"Sections found: {report['validation']['findings']['section_count']}")
            print(f"Links found: {report['validation']['findings']['link_count']}")
        elif report["status"] == "valid":
            f = report["validation"]["findings"]
            print(f"✓ Valid structure. Title: {f.get('title','?')}")
            print(f"  Sections: {f['section_count']}, Link items: {f['link_count']}")


if __name__ == "__main__":
    main()
