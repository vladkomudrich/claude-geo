#!/usr/bin/env python3
"""
fetch_page.py — Fetch a URL and report on its rendering profile.

Usage:
    python fetch_page.py <url> [--check-ssr] [--json]

Outputs:
    - raw HTML body text length
    - title
    - presence of meta tags
    - if --check-ssr: SSR verdict based on raw HTML
    - if --json: structured JSON output (else human-readable)

Used by geo-technical sub-agent.
"""
import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from html.parser import HTMLParser


DEFAULT_TIMEOUT = 15
USER_AGENT = "claude-geo/1.0 (+https://vdigital.app)"


class BodyTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_body = False
        self.in_script = False
        self.in_style = False
        self.body_chunks = []
        self.title = ""
        self.in_title = False
        self.has_main = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "body":
            self.in_body = True
        elif tag == "script":
            self.in_script = True
        elif tag == "style":
            self.in_style = True
        elif tag == "title":
            self.in_title = True
        elif tag == "main":
            self.has_main = True

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "body":
            self.in_body = False
        elif tag == "script":
            self.in_script = False
        elif tag == "style":
            self.in_style = False
        elif tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_script or self.in_style:
            return
        if self.in_title:
            self.title += data
        if self.in_body:
            text = data.strip()
            if text:
                self.body_chunks.append(text)


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
            status = resp.status
            headers = dict(resp.headers)
            raw = resp.read()
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}", "url": url}
    except urllib.error.URLError as e:
        return {"error": f"URL error: {e.reason}", "url": url}
    except Exception as e:
        return {"error": f"Fetch failed: {e}", "url": url}

    try:
        html = raw.decode("utf-8", errors="replace")
    except Exception:
        html = raw.decode("latin-1", errors="replace")

    parser = BodyTextExtractor()
    parser.feed(html)
    body_text = " ".join(parser.body_chunks)

    return {
        "url": url,
        "status": status,
        "headers": {k: v for k, v in headers.items() if k.lower() in {"content-type", "cf-ray", "server", "last-modified"}},
        "title": parser.title.strip(),
        "body_text": body_text,
        "body_text_length": len(body_text),
        "has_main": parser.has_main,
        "raw_html_length": len(html),
        "has_cf_ray": "cf-ray" in {k.lower() for k in headers.keys()},
    }


def check_ssr(result: dict) -> dict:
    """Heuristic SSR check based on raw HTML body content."""
    if "error" in result:
        return {"ssr_verdict": "unknown", "reason": result["error"]}

    body_len = result["body_text_length"]
    raw_len = result["raw_html_length"]

    if body_len < 200:
        return {
            "ssr_verdict": "js-only",
            "reason": f"Body text only {body_len} chars in raw HTML — likely JavaScript-rendered.",
            "severity": "critical",
        }
    if body_len < 500:
        return {
            "ssr_verdict": "partial",
            "reason": f"Body text {body_len} chars — sparse, possible partial SSR / shell.",
            "severity": "warning",
        }
    if body_len > 1000:
        return {
            "ssr_verdict": "ssr",
            "reason": f"Body text {body_len} chars — content is server-rendered.",
            "severity": "ok",
        }
    return {
        "ssr_verdict": "hybrid",
        "reason": f"Body text {body_len} chars — modest SSR content.",
        "severity": "warning",
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch URL and report rendering profile.")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--check-ssr", action="store_true", help="Include SSR verdict")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = fetch(args.url)

    if args.check_ssr and "error" not in result:
        result["ssr"] = check_ssr(result)

    if args.json:
        # Trim body_text in JSON output (too large) — keep length only.
        result.pop("body_text", None)
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(2)
        print(f"URL: {result['url']}")
        print(f"Status: {result['status']}")
        print(f"Title: {result['title']}")
        print(f"Raw HTML: {result['raw_html_length']} chars")
        print(f"Body text: {result['body_text_length']} chars")
        if result["has_cf_ray"]:
            print("Cloudflare: detected (cf-ray header present)")
            print("  → Reminder: verify AI Crawl Control in Cloudflare dashboard.")
        if args.check_ssr:
            ssr = result["ssr"]
            print(f"SSR verdict: {ssr['ssr_verdict'].upper()} — {ssr['reason']}")


if __name__ == "__main__":
    main()
