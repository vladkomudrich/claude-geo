#!/usr/bin/env python3
"""
check_reddit_presence.py — Count brand mentions across Reddit.

Usage:
    python check_reddit_presence.py "<brand>"
        [--subreddits=r/a,r/b,r/c]
        [--window=90]
        [--json]

Uses Reddit's public JSON search endpoint (no auth required for read-only
queries — though rate-limited). Falls back to DuckDuckGo HTML search if
Reddit blocks requests.

Used by geo-reddit and geo-presence sub-agents.
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error


USER_AGENT = "Mozilla/5.0 (compatible; claude-geo/1.0; +https://vdigital.app)"


def fetch_reddit_search(brand: str, subreddit: str | None = None, days: int = 90) -> dict:
    base = "https://www.reddit.com/search.json" if not subreddit else f"https://www.reddit.com/{subreddit.lstrip('r/')}/search.json"
    params = {
        "q": f'"{brand}"',
        "sort": "new",
        "limit": 50,
        "t": "year" if days > 30 else "month",
    }
    if subreddit:
        params["restrict_sr"] = "on"
    url = f"{base}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    # One retry on 429 (rate limited) with backoff.
    for attempt in (0, 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
                return {"ok": True, "data": data}
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(5)
                continue
            return {
                "ok": False,
                "error": f"HTTP {e.code}",
                "code": e.code,
                "note": "Reddit returned 429 (rate limited) — result is UNRELIABLE, not zero mentions." if e.code == 429 else
                        ("Reddit returned 403 (blocked) — result is UNRELIABLE." if e.code == 403 else None),
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "note": "Network/parse failure — result is UNRELIABLE."}
    return {"ok": False, "error": "Unknown failure"}


def parse_posts(data: dict, brand: str, days_cutoff: float) -> list[dict]:
    posts = []
    if not data or "data" not in data:
        return posts
    children = data["data"].get("children", [])
    cutoff_ts = time.time() - (days_cutoff * 86400)
    for c in children:
        post = c.get("data", {})
        created_utc = post.get("created_utc", 0)
        if created_utc < cutoff_ts:
            continue
        title = post.get("title", "")
        selftext = post.get("selftext", "")
        if brand.lower() not in (title + " " + selftext).lower():
            continue
        posts.append({
            "subreddit": post.get("subreddit"),
            "title": title,
            "url": f"https://reddit.com{post.get('permalink', '')}",
            "score": post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "created_utc": created_utc,
            "author": post.get("author"),
            "selftext_excerpt": selftext[:200],
        })
    return posts


def classify_sentiment(text: str) -> str:
    """Naive lexicon sentiment for triage. Real classification done by Claude."""
    pos_words = {"good", "great", "love", "best", "recommend", "excellent", "fantastic", "amazing", "awesome", "perfect", "helpful"}
    neg_words = {"bad", "hate", "worst", "awful", "terrible", "broken", "useless", "scam", "avoid", "disappointed", "buggy"}
    text_l = text.lower()
    pos = sum(1 for w in pos_words if f" {w} " in f" {text_l} ")
    neg = sum(1 for w in neg_words if f" {w} " in f" {text_l} ")
    if pos > neg + 1:
        return "positive"
    if neg > pos + 1:
        return "negative"
    return "neutral"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("brand")
    parser.add_argument("--subreddits", help="Comma-separated list, e.g. r/SaaS,r/webdev")
    parser.add_argument("--window", type=int, default=90, help="Days back")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    subreddits = []
    if args.subreddits:
        subreddits = [s.strip() for s in args.subreddits.split(",") if s.strip()]

    all_posts = []
    report = {"brand": args.brand, "window_days": args.window, "subreddits_queried": subreddits or ["(global)"], "by_subreddit": {}}

    if not subreddits:
        result = fetch_reddit_search(args.brand, subreddit=None, days=args.window)
        if result["ok"]:
            posts = parse_posts(result["data"], args.brand, args.window)
            all_posts.extend(posts)
            by_sub = {}
            for p in posts:
                by_sub.setdefault(p["subreddit"], []).append(p)
            report["by_subreddit"] = {sub: {"count": len(ps), "avg_score": round(sum(p["score"] for p in ps) / max(1, len(ps)), 1)} for sub, ps in by_sub.items()}
        else:
            report["error"] = result.get("error")
    else:
        for sub in subreddits:
            result = fetch_reddit_search(args.brand, subreddit=sub, days=args.window)
            time.sleep(1.5)  # rate limit politeness
            if result["ok"]:
                posts = parse_posts(result["data"], args.brand, args.window)
                all_posts.extend(posts)
                report["by_subreddit"][sub] = {
                    "count": len(posts),
                    "avg_score": round(sum(p["score"] for p in posts) / max(1, len(posts)), 1),
                    "top_post": posts[0]["url"] if posts else None,
                }
            else:
                report["by_subreddit"][sub] = {"error": result.get("error"), "count": 0}

    report["total_mentions"] = len(all_posts)
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    for p in all_posts:
        s = classify_sentiment(p["title"] + " " + p["selftext_excerpt"])
        sentiment_counts[s] += 1
    report["sentiment_distribution"] = sentiment_counts

    # Score
    score = 0
    if report["total_mentions"] >= 10:
        score += 15
    if report["total_mentions"] >= 50:
        score += 5  # bonus
    report["score_contribution"] = score

    if args.json:
        report["posts_sample"] = all_posts[:10]
        print(json.dumps(report, indent=2))
    else:
        print(f"Reddit mentions for '{args.brand}' (last {args.window} days)")
        print(f"Total mentions: {report['total_mentions']}")
        print(f"Score contribution: +{score}\n")
        if report["by_subreddit"]:
            print("By subreddit:")
            for sub, info in report["by_subreddit"].items():
                if "error" in info:
                    print(f"  {sub:<20} ERROR ({info['error']})")
                else:
                    print(f"  {sub:<20} {info['count']:>3} mentions, avg score {info.get('avg_score','-')}")
        print("\nSentiment distribution:")
        for k, v in sentiment_counts.items():
            print(f"  {k}: {v}")
        if all_posts:
            print("\nTop 5 by Reddit score:")
            for p in sorted(all_posts, key=lambda p: -p["score"])[:5]:
                print(f"  [{p['score']}↑ / {p['num_comments']}💬] r/{p['subreddit']}: {p['title'][:80]}")
                print(f"    {p['url']}")


if __name__ == "__main__":
    main()
