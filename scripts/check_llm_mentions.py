#!/usr/bin/env python3
"""
check_llm_mentions.py — Verify whether a brand is cited by AI engines for
category intent queries.

Usage:
    python check_llm_mentions.py "<brand>"
        --queries "q1|q2|q3|q4|q5"
        [--engine=all|chatgpt|claude|perplexity|aio]
        [--json]

Environment:
    OPENAI_API_KEY        — enables direct ChatGPT (web-search-enabled) calls.
    ANTHROPIC_API_KEY     — enables direct Claude calls.
    PERPLEXITY_API_KEY    — enables direct Perplexity API calls.

If a key is missing, the script falls back to public-search heuristics
(DuckDuckGo with site filters) and marks results as INDIRECT.

Used by geo-mentions sub-agent and `/geo verify llm-mention-*` commands.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import urllib.error


USER_AGENT = "claude-geo/1.0 (+https://vdigital.app)"


# Lexicons for naive sentiment + accuracy classification on captured passages.
# These produce coarse signals so the script can compute Pillar 5 bonus points
# without a separate LLM call. Sub-agents are expected to override with deeper
# classification when they have API access.
_POS = {"good","great","love","best","recommend","excellent","fantastic",
        "amazing","awesome","perfect","helpful","leading","top","trusted",
        "reliable","powerful","popular","preferred","strong"}
_NEG = {"bad","hate","worst","awful","terrible","broken","useless","scam",
        "avoid","disappointed","buggy","slow","lacking","weak","flawed",
        "limited","poor","subpar"}


def classify_sentiment(text: str) -> str:
    if not text:
        return "neutral"
    t = " " + text.lower() + " "
    pos = sum(1 for w in _POS if f" {w} " in t)
    neg = sum(1 for w in _NEG if f" {w} " in t)
    if pos > neg + 1:
        return "positive"
    if neg > pos + 1:
        return "negative"
    return "neutral"


def classify_accuracy(passage: str, brand: str) -> str:
    """Heuristic: if passage cites brand with at least one number / concrete
    detail (URL, year, version), call it 'likely-accurate'. If the passage is
    a vague mention without specifics, 'partial'. If the passage contradicts
    itself or contains 'maybe/might/probably', flag as 'partial'. Sub-agents
    should override with cross-reference against the actual product page."""
    if not passage:
        return "unknown"
    p = passage.lower()
    if any(hedge in p for hedge in (" maybe ", " might ", " probably ", " possibly ")):
        return "partial"
    has_number = bool(re.search(r"\d", passage))
    has_url = "http" in p or "www." in p
    has_year = bool(re.search(r"\b(202\d|201\d)\b", passage))
    if has_number or has_url or has_year:
        return "likely-accurate"
    return "partial"


def _post_json(url: str, headers: dict, payload: dict, timeout: int = 60) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        return {"_error": f"HTTP {e.code}", "_body": body[:500]}
    except Exception as e:
        return {"_error": str(e)}


def check_chatgpt(brand: str, query: str) -> dict:
    """Use OpenAI Responses API with web search if OPENAI_API_KEY set, else fallback."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return _fallback_search(brand, query, engine_hint="ChatGPT/OpenAI")
    # Use Responses API with web_search tool (model gpt-4o or similar)
    response = _post_json(
        "https://api.openai.com/v1/responses",
        {"Authorization": f"Bearer {key}"},
        {
            "model": "gpt-4o",
            "input": query,
            "tools": [{"type": "web_search_preview"}],
        },
        timeout=90,
    )
    if "_error" in response:
        return {"engine": "ChatGPT", "query": query, "mode": "api", "error": response["_error"], "cited": False}
    # Extract text content
    output_text = ""
    if "output" in response and isinstance(response["output"], list):
        for item in response["output"]:
            if item.get("type") == "message":
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        output_text += c.get("text", "")
    cited = brand.lower() in output_text.lower()
    passage = ""
    if cited:
        # Find sentence containing brand
        sentences = re.split(r"(?<=[\.!?])\s+", output_text)
        for s in sentences:
            if brand.lower() in s.lower():
                passage = s.strip()
                break
    return {
        "engine": "ChatGPT",
        "query": query,
        "mode": "api-web-search",
        "cited": cited,
        "passage": passage,
        "full_response_length": len(output_text),
    }


def check_claude(brand: str, query: str) -> dict:
    """Use Anthropic Messages API with web search if ANTHROPIC_API_KEY set."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return _fallback_search(brand, query, engine_hint="Claude/Anthropic")
    response = _post_json(
        "https://api.anthropic.com/v1/messages",
        {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
        {
            "model": "claude-sonnet-4-5",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": query}],
            "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
        },
        timeout=90,
    )
    if "_error" in response:
        return {"engine": "Claude", "query": query, "mode": "api", "error": response["_error"], "cited": False}
    output_text = ""
    for block in response.get("content", []):
        if block.get("type") == "text":
            output_text += block.get("text", "")
    cited = brand.lower() in output_text.lower()
    passage = ""
    if cited:
        sentences = re.split(r"(?<=[\.!?])\s+", output_text)
        for s in sentences:
            if brand.lower() in s.lower():
                passage = s.strip()
                break
    return {
        "engine": "Claude",
        "query": query,
        "mode": "api-web-search",
        "cited": cited,
        "passage": passage,
        "full_response_length": len(output_text),
    }


def check_perplexity(brand: str, query: str) -> dict:
    """Use Perplexity API if PERPLEXITY_API_KEY set."""
    key = os.environ.get("PERPLEXITY_API_KEY")
    if not key:
        return _fallback_search(brand, query, engine_hint="Perplexity")
    response = _post_json(
        "https://api.perplexity.ai/chat/completions",
        {"Authorization": f"Bearer {key}"},
        {
            "model": "sonar",
            "messages": [{"role": "user", "content": query}],
        },
        timeout=60,
    )
    if "_error" in response:
        return {"engine": "Perplexity", "query": query, "mode": "api", "error": response["_error"], "cited": False}
    output_text = ""
    for choice in response.get("choices", []):
        output_text += choice.get("message", {}).get("content", "")
    cited = brand.lower() in output_text.lower()
    passage = ""
    if cited:
        sentences = re.split(r"(?<=[\.!?])\s+", output_text)
        for s in sentences:
            if brand.lower() in s.lower():
                passage = s.strip()
                break
    return {
        "engine": "Perplexity",
        "query": query,
        "mode": "api",
        "cited": cited,
        "passage": passage,
        "full_response_length": len(output_text),
    }


def check_aio(brand: str, query: str) -> dict:
    """Google AI Overviews — no public API. Fall back to search-derived hint."""
    return _fallback_search(brand, query, engine_hint="Google AI Overviews",
                            note="Google AIO has no public API; result is INDIRECT (search heuristic).")


def _fallback_search(brand: str, query: str, engine_hint: str, note: str = "") -> dict:
    """Use DDG HTML search to find whether brand co-appears with query terms in top results."""
    url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {"engine": engine_hint, "query": query, "mode": "fallback-error", "error": str(e), "cited": False}

    titles = re.findall(r'class="result__a"[^>]*>([^<]+)</a>', html)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
    joined = " ".join(titles[:10]) + " " + " ".join(re.sub(r"<.*?>", "", s) for s in snippets[:10])
    cited = brand.lower() in joined.lower()
    return {
        "engine": engine_hint,
        "query": query,
        "mode": "indirect-search",
        "cited": cited,
        "passage": None,
        "note": note or "Result derived from public search, not direct LLM call. Mark as INDIRECT.",
    }


ENGINE_FUNCS = {
    "chatgpt": check_chatgpt,
    "claude": check_claude,
    "perplexity": check_perplexity,
    "aio": check_aio,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("brand")
    parser.add_argument("--queries", required=True, help="Pipe-separated queries: 'q1|q2|q3'")
    parser.add_argument("--engine", default="all", choices=["all"] + list(ENGINE_FUNCS.keys()))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    queries = [q.strip() for q in args.queries.split("|") if q.strip()]
    engines = list(ENGINE_FUNCS.keys()) if args.engine == "all" else [args.engine]

    report = {"brand": args.brand, "queries": queries, "engines": engines, "results": []}
    for engine in engines:
        for q in queries:
            result = ENGINE_FUNCS[engine](args.brand, q)
            report["results"].append(result)

    # Classify sentiment + accuracy on every cited passage.
    cited_results = []
    per_engine_cites = {e: 0 for e in engines}
    for r in report["results"]:
        if r.get("cited"):
            passage = r.get("passage") or ""
            r["sentiment"] = classify_sentiment(passage)
            r["accuracy"] = classify_accuracy(passage, args.brand)
            cited_results.append(r)
            eng = r["engine"]
            if "ChatGPT" in eng:
                per_engine_cites["chatgpt"] = per_engine_cites.get("chatgpt", 0) + 1
            elif "Claude" in eng:
                per_engine_cites["claude"] = per_engine_cites.get("claude", 0) + 1
            elif "Perplexity" in eng:
                per_engine_cites["perplexity"] = per_engine_cites.get("perplexity", 0) + 1
            elif "AI Overviews" in eng or "AIO" in eng:
                per_engine_cites["aio"] = per_engine_cites.get("aio", 0) + 1

    # Pillar 5 score: max 100 across engines + accuracy + sentiment bonuses.
    score = 0
    if per_engine_cites.get("chatgpt", 0) >= 3:
        score += 30
    elif per_engine_cites.get("chatgpt", 0) >= 1:
        score += 20
    if per_engine_cites.get("perplexity", 0) >= 3:
        score += 25
    elif per_engine_cites.get("perplexity", 0) >= 1:
        score += 15
    if per_engine_cites.get("aio", 0) >= 1:
        score += 15
    if per_engine_cites.get("claude", 0) >= 1:
        score += 10

    # Description factually correct on majority of citations (+10).
    if cited_results:
        accurate = sum(1 for r in cited_results if r.get("accuracy") == "likely-accurate")
        if accurate / len(cited_results) >= 0.5:
            score += 10
    # Sentiment neutral or positive on majority (+10).
    if cited_results:
        non_neg = sum(1 for r in cited_results if r.get("sentiment") in ("positive", "neutral"))
        if non_neg / len(cited_results) >= 0.5:
            score += 10

    report["per_engine_citations"] = per_engine_cites
    report["accuracy_distribution"] = {
        k: sum(1 for r in cited_results if r.get("accuracy") == k)
        for k in ("likely-accurate", "partial", "unknown")
    }
    report["sentiment_distribution"] = {
        k: sum(1 for r in cited_results if r.get("sentiment") == k)
        for k in ("positive", "neutral", "negative")
    }
    report["pillar_5_score"] = min(score, 100)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"LLM mention check for '{args.brand}'")
        print(f"Pillar 5 score: {report['pillar_5_score']}/100\n")
        for eng, cnt in per_engine_cites.items():
            print(f"  {eng:<12}: {cnt}/{len(queries)} queries cite brand")
        print()
        for r in report["results"]:
            tag = "✓" if r.get("cited") else "✗"
            mode = r.get("mode", "")
            print(f"{tag} [{r['engine']}] {r['query']}  ({mode})")
            if r.get("passage"):
                print(f"    → {r['passage'][:200]}")
            if r.get("note"):
                print(f"    ⓘ {r['note']}")


if __name__ == "__main__":
    main()
