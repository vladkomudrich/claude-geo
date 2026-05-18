#!/usr/bin/env python3
"""
check_youtube_presence.py — Check for YouTube videos mentioning a brand.

Usage:
    python check_youtube_presence.py "<brand>" [--json]

Uses YouTube's public search (HTML scrape; no API key needed). For deeper
metrics (view counts, channel sub counts) the YouTube Data API is required
and is not bundled here.

Used by geo-presence sub-agent.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
import urllib.error


USER_AGENT = "Mozilla/5.0 (compatible; claude-geo/1.0; +https://vdigital.app)"


def search_youtube(brand: str, limit: int = 20) -> list[dict]:
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(brand)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return [{"_error": str(e)}]

    # YouTube embeds ytInitialData as a JSON blob in a <script>
    match = re.search(r"var ytInitialData = (\{.*?\});</script>", html)
    if not match:
        return [{"_error": "ytInitialData not found in YouTube response — page structure changed or blocked. Result is unreliable."}]
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        return [{"_error": f"ytInitialData JSON parse failed: {e}. Result is unreliable."}]

    videos = []
    try:
        sections = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]
        for sec in sections:
            items = sec.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                v = item.get("videoRenderer")
                if not v:
                    continue
                video_id = v.get("videoId")
                title_runs = v.get("title", {}).get("runs", [])
                title = "".join(r.get("text", "") for r in title_runs)
                channel = v.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
                channel_url_fragment = v.get("ownerText", {}).get("runs", [{}])[0].get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url", "")
                description_runs = v.get("descriptionSnippet", {}).get("runs", []) if "descriptionSnippet" in v else []
                description = "".join(r.get("text", "") for r in description_runs)
                view_count = v.get("viewCountText", {}).get("simpleText", "")
                published = v.get("publishedTimeText", {}).get("simpleText", "")
                videos.append({
                    "video_id": video_id,
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "channel": channel,
                    "channel_url": f"https://www.youtube.com{channel_url_fragment}" if channel_url_fragment else None,
                    "description": description,
                    "view_count": view_count,
                    "published": published,
                })
                if len(videos) >= limit:
                    return videos
    except (KeyError, IndexError, TypeError) as e:
        # Surface the failure type rather than silently returning partial results.
        videos.append({"_error": f"YouTube ytInitialData traversal failed: {type(e).__name__}: {e}. Schema may have changed."})
    return videos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("brand")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    videos = search_youtube(args.brand)
    if videos and "_error" in videos[0]:
        print(json.dumps({"error": videos[0]["_error"]}, indent=2) if args.json else f"ERROR: {videos[0]['_error']}")
        sys.exit(2)

    # Classify: own-brand videos vs third-party (heuristic — channel name contains brand)
    brand_l = args.brand.lower()
    own_brand = [v for v in videos if brand_l in (v.get("channel") or "").lower()]
    third_party = [v for v in videos if v not in own_brand]

    score = 0
    if len(third_party) >= 5:
        score += 10
    elif len(third_party) >= 1:
        score += 5
    if len(own_brand) >= 12:
        score += 5

    report = {
        "brand": args.brand,
        "total_results": len(videos),
        "own_brand_videos": len(own_brand),
        "third_party_videos": len(third_party),
        "score_contribution": score,
        "videos_sample": videos[:10],
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"YouTube presence for '{args.brand}'")
        print(f"Total results: {len(videos)} (own-brand: {len(own_brand)}, third-party: {len(third_party)})")
        print(f"Score contribution: +{score}\n")
        print("Top 5 results:")
        for v in videos[:5]:
            owner_tag = "[OWN]" if v in own_brand else "[3rd]"
            print(f"  {owner_tag} {v['title'][:80]}")
            print(f"        channel: {v['channel']} | {v.get('view_count','')} | {v.get('published','')}")
            print(f"        {v['url']}")


if __name__ == "__main__":
    main()
