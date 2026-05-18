#!/usr/bin/env python3
"""
check_robots_txt.py — Audit robots.txt for AI crawler access.

Usage:
    python check_robots_txt.py <url> [--bots=all|openai|claude|perplexity|google] [--json]

Outputs:
    - per-bot Allow / Disallow / Implicit-allow status
    - flag for retired bots (anthropic-ai, claude-web)
    - presence of Cloudflare-related headers via separate request
    - Pillar 1 sub-scores

Used by geo-technical sub-agent and `/geo verify robots-txt` command.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
import urllib.error
from urllib.robotparser import RobotFileParser


USER_AGENT = "claude-geo/1.0 (+https://vdigital.app)"

ALL_BOTS = {
    "openai": [
        ("GPTBot", "training"),
        ("OAI-SearchBot", "search index"),
        ("ChatGPT-User", "user-initiated"),
    ],
    "claude": [
        ("ClaudeBot", "training (supports Crawl-delay)"),
        ("Claude-User", "user-initiated"),
        ("Claude-SearchBot", "search index"),
    ],
    "perplexity": [
        ("PerplexityBot", "main"),
        ("Perplexity-User", "user-initiated"),
    ],
    "google": [
        ("Google-Extended", "Gemini/AIO training control"),
        ("Googlebot", "standard search"),
    ],
    "microsoft": [
        ("bingbot", "standard"),
    ],
    "optional": [
        ("Applebot", "Apple Intelligence"),
        ("Applebot-Extended", "Apple Intelligence training"),
        ("Meta-ExternalAgent", "Meta AI"),
        ("MistralAI-User", "Mistral"),
        ("Amazonbot", "Amazon"),
        ("CCBot", "Common Crawl"),
        ("Bytespider", "ByteDance / TikTok"),
        ("cohere-ai", "Cohere"),
    ],
}

RETIRED_BOTS = [
    ("anthropic-ai", "Retired July 2024 — robots.txt rules ineffective."),
    ("claude-web", "Retired July 2024 — robots.txt rules ineffective."),
]


def fetch_robots(url: str) -> dict:
    parsed = urllib.parse.urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    req = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            headers = dict(resp.headers)
            return {"url": robots_url, "status": resp.status, "text": text, "headers": headers}
    except urllib.error.HTTPError as e:
        return {"url": robots_url, "error": f"HTTP {e.code}", "missing": e.code == 404}
    except Exception as e:
        return {"url": robots_url, "error": str(e)}


def check_bot(robots_text: str, bot_name: str) -> str:
    """Return 'allowed', 'disallowed', 'implicit-allowed', or 'implicit-disallowed'.

    Real-world robots.txt uses many spacing/casing variants:
        User-agent: GPTBot
        User-Agent:  GPTBot
        user-agent:GPTBot
    Detect the explicit section using a permissive regex.
    """
    rp = RobotFileParser()
    rp.parse(robots_text.splitlines())
    # Permissive section detection — case-insensitive, any whitespace.
    pattern = re.compile(
        r"^\s*user-agent\s*:\s*" + re.escape(bot_name) + r"\s*(#.*)?$",
        re.IGNORECASE | re.MULTILINE,
    )
    has_section = bool(pattern.search(robots_text))
    if has_section:
        return "allowed" if rp.can_fetch(bot_name, "/") else "disallowed"
    # No explicit section — falls under User-agent: *
    if rp.can_fetch(bot_name, "/"):
        return "implicit-allowed"
    return "implicit-disallowed"


def score_pillar(report: dict) -> int:
    """Compute the technical pillar score per scoring-rubric.md."""
    score = 0

    def is_allowed(bot):
        s = report["bots"].get(bot, {}).get("status", "")
        return s in {"allowed", "implicit-allowed"}

    if is_allowed("GPTBot") or is_allowed("OAI-SearchBot"):
        score += 15
    if is_allowed("ClaudeBot") and is_allowed("Claude-SearchBot"):
        score += 15
    if is_allowed("PerplexityBot") and is_allowed("Perplexity-User"):
        score += 10
    if is_allowed("Google-Extended"):
        score += 5
    # Bytespider / cohere-ai documented either way (presence in robots.txt)
    bots_text = report.get("raw_text", "").lower()
    if "bytespider" in bots_text or "cohere-ai" in bots_text:
        score += 5

    # cap at 50 for robots-only signals (rest comes from SSR + llms.txt + sitemap + Cloudflare in other scripts)
    return min(score, 50)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--bots", default="all",
                        choices=["all", "openai", "claude", "perplexity", "google"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    fetched = fetch_robots(args.url)
    if "error" in fetched:
        if args.json:
            print(json.dumps({"error": fetched["error"], "url": fetched["url"]}, indent=2))
        else:
            print(f"ERROR fetching {fetched['url']}: {fetched['error']}")
            if fetched.get("missing"):
                print("robots.txt missing — Cloudflare/CDN default behavior may apply.")
        sys.exit(0 if fetched.get("missing") else 2)

    text = fetched["text"]
    families = [args.bots] if args.bots != "all" else list(ALL_BOTS.keys())
    report = {"url": fetched["url"], "bots": {}, "retired_present": [], "raw_text": text}

    for family in families:
        for bot_name, purpose in ALL_BOTS[family]:
            status = check_bot(text, bot_name)
            report["bots"][bot_name] = {"family": family, "purpose": purpose, "status": status}

    for retired, note in RETIRED_BOTS:
        if retired.lower() in text.lower():
            report["retired_present"].append({"bot": retired, "note": note})

    report["pillar_1_partial_score"] = score_pillar(report)

    if args.json:
        report.pop("raw_text", None)
        print(json.dumps(report, indent=2))
    else:
        print(f"robots.txt for {report['url']}")
        print(f"Pillar 1 partial score (robots only): {report['pillar_1_partial_score']}/50")
        print()
        print(f"{'Bot':<25} {'Family':<12} {'Status':<22} Purpose")
        print("-" * 90)
        for bot_name, info in report["bots"].items():
            status_marker = "✓" if "allowed" in info["status"] else "✗"
            print(f"{bot_name:<25} {info['family']:<12} {status_marker} {info['status']:<20} {info['purpose']}")
        if report["retired_present"]:
            print()
            print("⚠ Retired bots referenced (harmless, but obsolete):")
            for r in report["retired_present"]:
                print(f"  - {r['bot']}: {r['note']}")


if __name__ == "__main__":
    main()
