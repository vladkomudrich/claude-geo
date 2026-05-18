# Changelog

All notable changes to `claude-geo` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_Nothing yet — open an issue or PR if you find one._

## [1.0.0] — 2026-05-18

Initial public release. A modular Generative Engine Optimization plugin
for Claude Code, designed to coexist with [claude-seo](https://github.com/AgriciDaniel/claude-seo).

### Added

#### Sub-skills (12)

- `geo` — orchestrator and command router.
- `geo-audit` — full audit, spawns all sub-agents in parallel.
- `geo-technical` — robots.txt for AI bots, llms.txt, SSR vs JS-only, sitemap, Cloudflare AI Crawl Control.
- `geo-content` — CITABLE framework scoring (BLUF, intent, third-party, answer grounding, block structure, latest, entity), tables, lists, sentence length, front-loading, passage segmentation.
- `geo-schema` — JSON-LD audit with `knowsAbout`, `sameAs`, `FAQPage` for AI extraction, entity chain depth.
- `geo-presence` — interview + automated verification across Wikipedia/Wikidata, G2/Capterra/Trustpilot, Reddit, YouTube, LinkedIn.
- `geo-mentions` — real LLM mention checks across ChatGPT, Claude, Perplexity, Google AI Overviews.
- `geo-reddit` — Reddit presence audit + 6-step organic playbook.
- `geo-trust` — Wikipedia/Wikidata + review-aggregator listings with the **G2 4.0 rule** flagged as a hard ChatGPT filter.
- `geo-plan` — sequenced 90-day GEO roadmap combining technical + creative actions.
- `geo-verify` — technique-level verifier dispatcher for after-the-fact validation.
- `geo-report` — generates Markdown + dual-HTML reports (presentation deck + scrollable technical guide).

#### Sub-agents (7)

`geo-technical`, `geo-content`, `geo-schema`, `geo-presence`, `geo-mentions`, `geo-reddit`, `geo-reporter`.

#### Verifier scripts (9 real-check + 3 utility, all `python3` stdlib only)

- `check_robots_txt.py` — AI crawler access detection (OpenAI three-bot, Anthropic three-bot framework, Perplexity, Google-Extended, Apple/Meta/Mistral/Amazon optional).
- `check_llms_txt.py` — `/llms.txt` presence and structural validation.
- `check_schema.py` — JSON-LD extraction, Organization with `knowsAbout`/`sameAs`, FAQPage, entity chain depth, deprecated-type detection.
- `check_content_structure.py` — tables, lists, sentence length, passage segmentation, front-loading, visible date, authoritative outbound links. Supports `--check=tables|lists|sentences|bluf|frontload|passages|date` for focused sub-checks.
- `check_wikipedia.py` — Wikipedia + Wikidata search via official APIs (no key required).
- `check_trust_sites.py` — G2, Capterra, Trustpilot, Software Advice, GetApp, TrustRadius listing discovery.
- `check_reddit_presence.py` — 90-day mention count across target subreddits with naive sentiment classification. 429 retry with backoff.
- `check_youtube_presence.py` — third-party + own-channel video search.
- `check_llm_mentions.py` — real LLM citation checks via OpenAI/Anthropic/Perplexity APIs (when keys present) with WebSearch fallback. Sentiment + accuracy classification per cited passage.
- `fetch_page.py` — page fetcher with SSR-vs-JS-only verdict.
- `score_geo.py` — five-pillar weighted aggregation with grade A-F and top-5 action ranking by leverage.
- `generate_report.py` — template renderer for Markdown + dual-HTML formats with `</script>` injection-safe JSON embed.

#### Report templates (3)

- `templates/report-audit.md` — Markdown audit document.
- `templates/report-presentation.html` — slide deck (keyboard-navigable, Chart.js, dark theme).
- `templates/report-guide.html` — sidebar-navigated technical guide with scroll-spy.

#### References (8, loaded on-demand)

- `geo-research-2026.md` — condensed evidence base for every claim with primary/secondary/estimate source tags.
- `platforms-2026.md` — per-platform optimization guide (ChatGPT, Claude, Perplexity, Google AIO, AI Mode, Copilot).
- `citable-framework.md` — CITABLE framework with examples and per-letter pass thresholds.
- `scoring-rubric.md` — full five-pillar scoring algorithm.
- `creative-techniques.md` — non-technical GEO playbook (Wikipedia, Reddit, G2/Capterra, YouTube, PR).
- `reddit-strategy.md` — Reddit deep dive with 6-step organic playbook.
- `compatibility-with-seo.md` — explicit ownership map vs claude-seo.
- `author.md` — canonical author footer (single source of truth, consumed by `generate_report.py`).

### Compatibility

- Different command namespace from `claude-seo` (`/geo *` vs `/seo *`) — no collision.
- Different output filename convention (`GEO-Audit-*`, `GEO-Presentation-*`, `GEO-Guide-*` vs claude-seo's `GEO-ANALYSIS.md`) — no overwrite.
- Both plugins can be installed and used simultaneously.
- Recommendations are additive: `claude-geo` never instructs removing schema or robots.txt rules that `claude-seo` would add.

### Quality gates enforced

- Never recommend `HowTo` schema (rich results retired September 2023).
- Never recommend `anthropic-ai` or `claude-web` in robots.txt (retired July 2024).
- Flag aggregate review score < 4.0 on G2/Capterra/Trustpilot as **Critical** (hard ChatGPT filter in competitive queries).
- Flag JavaScript-only sites as **Critical** (AI crawlers do not execute JS).
- Recommend `FAQPage` schema only with explicit caveat that Google rich results were deprecated 7 May 2026.
- Recommend `/llms.txt` for developer-tool products only; explicitly low priority for non-developer sites.

### Notes

- All script paths use `${CLAUDE_PLUGIN_ROOT}` so the plugin works from any working directory once installed at `~/.claude/plugins/claude-geo/`.
- Python stdlib only — no `requirements.txt` needed.
- API keys for direct LLM mention checks (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `PERPLEXITY_API_KEY`) are optional; the plugin falls back to WebSearch with explicit `INDIRECT` marking.
- Scrapers (Reddit, YouTube, DuckDuckGo) surface `_error` / `_warning` markers when public HTML/JSON structures change, so callers can distinguish "scraper broken" from "genuine zero result".

[Unreleased]: https://github.com/vladkomudrich/claude-geo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/vladkomudrich/claude-geo/releases/tag/v1.0.0
