#!/usr/bin/env python3
"""
check_content_structure.py — Score a page on content citability signals.

Usage:
    python check_content_structure.py <url>
        [--check=tables|lists|sentences|bluf|frontload|passages|date|all]
        [--json]

Mechanical metrics computed:
  - Table count
  - List count + items per list
  - Avg sentence length (words)
  - Median paragraph length (words)
  - Self-contained 50-150 word passages
  - Position of first numeric statistic (which third)
  - Visible date string presence
  - H1/H2/H3 hierarchy
  - Question-style H2/H3 ratio
  - Page word count
  - Outbound authoritative link count

Used by geo-content sub-agent.
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


class StructureExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_body = False
        self.in_script = False
        self.in_style = False
        self.in_table = 0
        self.in_ul = 0
        self.in_ol = 0
        self.in_li = 0
        self.in_h1 = 0
        self.in_h2 = 0
        self.in_h3 = 0
        self.in_p = 0
        self.in_a = 0
        self.current_a_href = ""
        self.current_a_text = []
        self.tables = 0
        self.lists = []  # list of int (items per list)
        self.current_list_items = 0
        self.h1_texts = []
        self.h2_texts = []
        self.h3_texts = []
        self.paragraphs = []
        self.current_p = []
        self.current_heading = []
        self.body_text = []
        self.outbound_links = []
        self.current_outbound = False

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t == "body":
            self.in_body = True
        elif t == "script":
            self.in_script = True
        elif t == "style":
            self.in_style = True
        elif t == "table":
            self.in_table += 1
            self.tables += 1
        elif t == "ul":
            self.in_ul += 1
            self.current_list_items = 0
        elif t == "ol":
            self.in_ol += 1
            self.current_list_items = 0
        elif t == "li":
            self.in_li += 1
            if self.in_ul or self.in_ol:
                self.current_list_items += 1
        elif t == "h1":
            self.in_h1 += 1
            self.current_heading = []
        elif t == "h2":
            self.in_h2 += 1
            self.current_heading = []
        elif t == "h3":
            self.in_h3 += 1
            self.current_heading = []
        elif t == "p":
            self.in_p += 1
            self.current_p = []
        elif t == "a":
            self.in_a += 1
            href = ""
            for k, v in attrs:
                if k.lower() == "href":
                    href = v
                    break
            self.current_a_href = href
            self.current_a_text = []

    def handle_endtag(self, tag):
        t = tag.lower()
        if t == "body":
            self.in_body = False
        elif t == "script":
            self.in_script = False
        elif t == "style":
            self.in_style = False
        elif t == "table":
            self.in_table = max(0, self.in_table - 1)
        elif t == "ul":
            self.in_ul = max(0, self.in_ul - 1)
            self.lists.append(self.current_list_items)
            self.current_list_items = 0
        elif t == "ol":
            self.in_ol = max(0, self.in_ol - 1)
            self.lists.append(self.current_list_items)
            self.current_list_items = 0
        elif t == "li":
            self.in_li = max(0, self.in_li - 1)
        elif t == "h1":
            self.in_h1 = max(0, self.in_h1 - 1)
            self.h1_texts.append(" ".join(self.current_heading).strip())
        elif t == "h2":
            self.in_h2 = max(0, self.in_h2 - 1)
            self.h2_texts.append(" ".join(self.current_heading).strip())
        elif t == "h3":
            self.in_h3 = max(0, self.in_h3 - 1)
            self.h3_texts.append(" ".join(self.current_heading).strip())
        elif t == "p":
            self.in_p = max(0, self.in_p - 1)
            text = " ".join(self.current_p).strip()
            if text:
                self.paragraphs.append(text)
            self.current_p = []
        elif t == "a":
            self.in_a = max(0, self.in_a - 1)
            text = "".join(self.current_a_text).strip()
            if self.current_a_href and self.current_a_href.startswith("http"):
                self.outbound_links.append({"href": self.current_a_href, "text": text})
            self.current_a_href = ""

    def handle_data(self, data):
        if self.in_script or self.in_style:
            return
        if self.in_body:
            self.body_text.append(data)
        if self.in_p:
            self.current_p.append(data)
        if self.in_h1 or self.in_h2 or self.in_h3:
            self.current_heading.append(data)
        if self.in_a:
            self.current_a_text.append(data)


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


def sentence_split(text: str) -> list[str]:
    # Simple heuristic: split on `.!?` followed by whitespace + capital letter.
    sentences = re.split(r"(?<=[\.!?])\s+(?=[A-Z(])", text)
    return [s.strip() for s in sentences if s.strip()]


def is_question_heading(h: str) -> bool:
    h = h.strip().lower()
    if h.endswith("?"):
        return True
    starters = ("what ", "why ", "how ", "when ", "where ", "who ", "which ", "is ", "are ", "should ", "can ", "do ", "does ")
    return any(h.startswith(s) for s in starters)


def detect_date(text: str) -> str | None:
    patterns = [
        r"(Last [Uu]pdated|Updated|Published|Reviewed)[\s:]+([A-Z][a-z]+ \d{1,2},? \d{4})",
        r"(Last [Uu]pdated|Updated|Published|Reviewed)[\s:]+(\d{4}-\d{2}-\d{2})",
        r"(\d{4}-\d{2}-\d{2})",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(0)
    return None


def analyze(html: str) -> dict:
    ext = StructureExtractor()
    ext.feed(html)
    body = " ".join(ext.body_text)
    body = re.sub(r"\s+", " ", body).strip()
    sentences = sentence_split(body)
    words = body.split()
    word_count = len(words)
    avg_sentence_len = (sum(len(s.split()) for s in sentences) / len(sentences)) if sentences else 0
    list_with_5plus = sum(1 for l in ext.lists if l >= 5)
    questionish_h2 = sum(1 for h in ext.h2_texts if is_question_heading(h))
    questionish_h3 = sum(1 for h in ext.h3_texts if is_question_heading(h))
    paragraph_word_counts = [len(p.split()) for p in ext.paragraphs]
    median_para = sorted(paragraph_word_counts)[len(paragraph_word_counts) // 2] if paragraph_word_counts else 0
    self_contained_passages = sum(1 for w in paragraph_word_counts if 50 <= w <= 150)

    # First-number position
    first_num_match = re.search(r"\d+([,.]\d+)?(%|x|×)?", body)
    if first_num_match and word_count > 0:
        char_pos = first_num_match.start()
        rel_pos = char_pos / max(1, len(body))
        front_loaded = rel_pos <= 0.33
    else:
        rel_pos = None
        front_loaded = False

    # Outbound authoritative links — heuristic: well-known domains
    authoritative_domains = {
        "wikipedia.org", "wikidata.org", "g2.com", "capterra.com", "trustpilot.com",
        "github.com", "linkedin.com", "youtube.com", "x.com", "twitter.com",
        "arxiv.org", "doi.org", "nature.com", "sciencedirect.com", "ieee.org",
        "developers.google.com", "schema.org", "w3.org",
        "nytimes.com", "wsj.com", "ft.com", "forbes.com", "techcrunch.com",
        "stripe.com", "openai.com", "anthropic.com", "perplexity.ai",
    }
    authoritative_outbound = []
    for link in ext.outbound_links:
        try:
            host = urllib.parse.urlparse(link["href"]).netloc.lower()
            for d in authoritative_domains:
                if d in host:
                    authoritative_outbound.append(link["href"])
                    break
        except Exception:
            continue

    return {
        "word_count": word_count,
        "char_count": len(body),
        "tables": ext.tables,
        "list_count": len(ext.lists),
        "lists_with_5plus_items": list_with_5plus,
        "avg_sentence_length_words": round(avg_sentence_len, 1),
        "median_paragraph_words": median_para,
        "self_contained_passages_50_150_words": self_contained_passages,
        "h1_count": len(ext.h1_texts),
        "h2_count": len(ext.h2_texts),
        "h3_count": len(ext.h3_texts),
        "question_style_h2_ratio": round(questionish_h2 / max(1, len(ext.h2_texts)), 2),
        "question_style_h3_ratio": round(questionish_h3 / max(1, len(ext.h3_texts)), 2),
        "first_number_position_pct": round(rel_pos * 100, 1) if rel_pos is not None else None,
        "front_loaded": front_loaded,
        "visible_date": detect_date(body),
        "outbound_link_count": len(ext.outbound_links),
        "authoritative_outbound_count": len(authoritative_outbound),
        "authoritative_outbound_examples": authoritative_outbound[:5],
    }


def score(metrics: dict) -> int:
    s = 0
    if metrics["tables"] >= 3:
        s += 15
    elif metrics["tables"] >= 1:
        s += 10
    if metrics["list_count"] >= 8:
        s += 15
    elif metrics["lists_with_5plus_items"] >= 1:
        s += 10
    if metrics["avg_sentence_length_words"] and metrics["avg_sentence_length_words"] <= 10:
        s += 15
    elif metrics["avg_sentence_length_words"] and metrics["avg_sentence_length_words"] <= 12:
        s += 10
    if metrics["front_loaded"]:
        s += 10
    if metrics["self_contained_passages_50_150_words"] >= 3:
        s += 10
    if metrics["visible_date"]:
        s += 5
    # Q-style H2 ratio bonus
    if metrics["question_style_h2_ratio"] >= 0.7:
        s += 10
    # Outbound authoritative links
    if metrics["authoritative_outbound_count"] >= 2:
        s += 10
    # Long page bonus
    if metrics["word_count"] >= 1500:
        s += 5
    return min(s, 100)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--check", default="all",
                        choices=["all", "tables", "lists", "sentences", "bluf", "frontload", "passages", "date"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    fetched = fetch(args.url)
    if "error" in fetched:
        print(json.dumps({"error": fetched["error"]}, indent=2) if args.json else f"ERROR: {fetched['error']}")
        sys.exit(2)

    metrics = analyze(fetched["html"])
    metrics["score"] = score(metrics)
    metrics["url"] = args.url
    metrics["check"] = args.check

    # Sub-check filtering — focus output on the requested signal.
    SUB_CHECKS = {
        "tables": {
            "fields": ["tables"],
            "verdict_key": "tables",
            "thresholds": [(3, "PASS — 3+ tables (max signal)"),
                           (1, "PARTIAL — at least 1 table"),
                           (0, "FAIL — no tables")],
        },
        "lists": {
            "fields": ["list_count", "lists_with_5plus_items"],
            "verdict_key": "lists_with_5plus_items",
            "thresholds": [(8, "PASS — 8+ list sections"),
                           (1, "PARTIAL — at least 1 list with 5+ items"),
                           (0, "FAIL — no qualifying lists")],
        },
        "sentences": {
            "fields": ["avg_sentence_length_words"],
            "verdict_key": "avg_sentence_length_words",
            "thresholds_lt": [(10, "PASS — avg sentence ≤ 10 words"),
                              (12, "PARTIAL — avg sentence ≤ 12 words")],
            "fail_msg": "FAIL — avg sentence > 12 words",
        },
        "bluf": {
            "fields": ["front_loaded", "first_number_position_pct"],
            "verdict_key": "front_loaded",
        },
        "frontload": {
            "fields": ["front_loaded", "first_number_position_pct"],
            "verdict_key": "front_loaded",
        },
        "passages": {
            "fields": ["self_contained_passages_50_150_words"],
            "verdict_key": "self_contained_passages_50_150_words",
            "thresholds": [(3, "PASS — 3+ self-contained passages"),
                           (1, "PARTIAL — at least 1"),
                           (0, "FAIL — no 50-150 word self-contained passages")],
        },
        "date": {
            "fields": ["visible_date"],
            "verdict_key": "visible_date",
        },
    }

    if args.check != "all" and args.check in SUB_CHECKS:
        cfg = SUB_CHECKS[args.check]
        value = metrics.get(cfg["verdict_key"])
        if "thresholds" in cfg:
            verdict = next((msg for t, msg in cfg["thresholds"] if (value or 0) >= t), cfg["thresholds"][-1][1])
        elif "thresholds_lt" in cfg:
            verdict = next((msg for t, msg in cfg["thresholds_lt"] if value and value <= t), cfg.get("fail_msg", "FAIL"))
        elif cfg["verdict_key"] in ("front_loaded",):
            verdict = "PASS — key facts in first third" if value else "FAIL — front-load key statistics"
        elif cfg["verdict_key"] == "visible_date":
            verdict = f"PASS — visible date: {value}" if value else "FAIL — no visible date string"
        else:
            verdict = "—"
        focused = {k: metrics[k] for k in cfg["fields"]}
        focused["verdict"] = verdict
        focused["check"] = args.check
        focused["url"] = args.url
        if args.json:
            print(json.dumps(focused, indent=2))
        else:
            print(f"Content sub-check: {args.check.upper()}  ({args.url})")
            print(f"Verdict: {verdict}")
            for f in cfg["fields"]:
                print(f"  {f}: {metrics[f]}")
        return

    if args.json:
        print(json.dumps(metrics, indent=2))
    else:
        print(f"Content structure for {args.url}")
        print(f"Pillar 2 score: {metrics['score']}/100\n")
        print(f"Word count: {metrics['word_count']} ({metrics['char_count']} chars)")
        print(f"Tables: {metrics['tables']}")
        print(f"Lists: {metrics['list_count']} (with 5+ items: {metrics['lists_with_5plus_items']})")
        print(f"Avg sentence length: {metrics['avg_sentence_length_words']} words")
        print(f"Median paragraph: {metrics['median_paragraph_words']} words")
        print(f"50-150-word self-contained passages: {metrics['self_contained_passages_50_150_words']}")
        print(f"H1 / H2 / H3: {metrics['h1_count']} / {metrics['h2_count']} / {metrics['h3_count']}")
        print(f"Question-style H2 ratio: {metrics['question_style_h2_ratio']}")
        print(f"First number at: {metrics['first_number_position_pct']}% of page  → front-loaded: {metrics['front_loaded']}")
        print(f"Visible date: {metrics['visible_date'] or 'NOT FOUND'}")
        print(f"Authoritative outbound links: {metrics['authoritative_outbound_count']}")


if __name__ == "__main__":
    main()
