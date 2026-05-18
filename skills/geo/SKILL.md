---
name: geo
description: >
  Generative Engine Optimization (GEO) — analyze and improve how AI engines
  (ChatGPT, Claude, Perplexity, Google AI Overviews + AI Mode, Gemini 3,
  Copilot) cite and recommend a brand or product. Full audits, technical
  checks (robots.txt for AI crawlers, llms.txt, JSON-LD schema with
  knowsAbout/sameAs, SSR), content structure (CITABLE/BLUF, tables, lists,
  passage length), off-site presence (Reddit, Wikipedia, G2/Capterra,
  YouTube), real verification of brand mentions in LLM answers, and
  Markdown + dual-HTML reports (presentation deck + technical guide).
  Triggers on: GEO, AEO, generative engine optimization, AI search
  optimization, AI Overviews, AI Mode, ChatGPT citations, Perplexity,
  Claude citations, Gemini, LLM visibility, brand mentions in AI,
  llms.txt, CITABLE, BLUF, AI crawlers, agentic commerce.
user-invokable: true
argument-hint: "[command] [url|brand]"
license: MIT
metadata:
  author: Digital Vlad
  author-url: "https://vdigital.app/"
  author-telegram: "https://t.me/vladi9ital"
  author-youtube: "https://www.youtube.com/@vladi9ital"
  version: "1.0.0"
  category: geo
  coexists-with: claude-seo
---

# GEO: Generative Engine Optimization Orchestrator

**Invocation:** `/geo $1 $2` where `$1` is a sub-command and `$2` is a URL or brand name.

**Scope.** GEO is the layer **on top of SEO** that controls how AI engines cite,
quote, and recommend a brand. This skill does not replace traditional SEO. If a
user needs core SEO (Core Web Vitals, technical crawlability, on-page audits,
backlinks, local SEO), defer to `claude-seo`. GEO and SEO command namespaces
are intentionally separate: `/seo` vs `/geo`. They can be installed together
and used in the same workflow.

## Quick Reference

| Command | What it does |
|---------|--------------|
| `/geo help` | Show this overview — capabilities, commands, recommended workflow, where to start |
| `/geo audit <url>` | Full GEO audit — runs technical, content, schema, presence checks in parallel, produces score + report |
| `/geo technical <url>` | Technical GEO only: robots.txt (AI crawlers), llms.txt, SSR vs CSR, page speed for crawlers |
| `/geo content <url>` | Content structure audit: CITABLE, BLUF, tables, lists, passage length, sentence length, front-loading |
| `/geo schema <url>` | JSON-LD audit for GEO: Organization (knowsAbout, sameAs), FAQPage (for AI), Product, entity chain |
| `/geo presence <brand>` | Off-site presence interview + automated checks across Wikipedia, Reddit, G2/Capterra, YouTube |
| `/geo mentions <brand>` | Real brand-mention check across ChatGPT, Claude, Perplexity for a curated set of queries |
| `/geo reddit <brand>` | Reddit presence audit + organic posting strategy (subreddit targeting, weekly cadence) |
| `/geo trust <brand>` | Wikipedia / Wikidata / G2 / Capterra / Trustpilot presence + score check |
| `/geo plan <url\|brand>` | Strategic GEO roadmap: 90-day plan combining technical + creative techniques |
| `/geo verify <technique> <url>` | Verify a specific technique was applied (e.g. `verify schema-knowsabout`, `verify llms-txt`) |
| `/geo report <type> <url>` | Generate a report. Types: `md`, `html-guide` (technical), `all` |

## `/geo help` — What This Plugin Does

When the user invokes `/geo help`, `/geo` (no args), or `/geo --help`, respond
with this exact briefing (substitute the current date where shown):

```
claude-geo — Generative Engine Optimization for Claude Code

WHAT IT DOES
  Audits and improves how AI engines (ChatGPT, Claude, Perplexity,
  Google AI Overviews + AI Mode, Gemini 3, Copilot) cite and recommend
  your brand. Works alongside claude-seo, never overlaps with it.

FIVE-PILLAR SCORING (0-100, weighted)
  20%  Technical accessibility   robots.txt for AI bots, llms.txt, SSR
  25%  Content citability       CITABLE / BLUF / tables / lists / sentences
  15%  Schema & entities        JSON-LD knowsAbout / sameAs / FAQPage
  25%  Off-site presence        Wikipedia, G2/Capterra (4.0 rule), Reddit, YouTube
  15%  Real-world citations     Verified mentions in actual LLM answers

EVERY SIGNAL HAS A REAL VERIFIER SCRIPT — not a hypothesis.

THREE WAYS TO USE IT

  1. Start with a full audit
     /geo audit https://your-site.com
     → Produces MD audit + HTML presentation deck + HTML technical guide.

  2. Audit one pillar at a time
     /geo technical <url>     robots.txt + llms.txt + SSR
     /geo content   <url>     CITABLE framework + structural metrics
     /geo schema    <url>     JSON-LD audit for AI extraction
     /geo presence  <brand>   Wikipedia / G2 / Reddit / YouTube
     /geo mentions  <brand>   Real ChatGPT/Claude/Perplexity citation check

  3. Plan, do, verify
     /geo plan <url>                       90-day roadmap (technical + creative)
     /geo verify <technique> <url>         confirm a change actually landed
     /geo report all <url>                 regenerate reports after changes

VERIFY TECHNIQUES (after implementing changes)
  /geo verify schema-knowsabout <url>
  /geo verify schema-sameas <url>
  /geo verify content-bluf <url>
  /geo verify content-tables <url>
  /geo verify content-front-loading <url>
  /geo verify robots-txt <url>
  /geo verify ssr <url>
  /geo verify llms-txt <url>
  /geo verify wikipedia <brand>
  /geo verify g2-rating <brand>
  /geo verify reddit-presence <brand>
  /geo verify llm-mention-chatgpt <brand>
  (full list in skills/geo-verify/SKILL.md)

OPTIONAL API KEYS (for direct LLM mention checks)
  OPENAI_API_KEY       direct ChatGPT (web-search enabled)
  ANTHROPIC_API_KEY    direct Claude
  PERPLEXITY_API_KEY   direct Perplexity
  (Missing keys → falls back to WebSearch, marked INDIRECT.)

KEY HARD RULES (enforced automatically)
  ✗ HowTo schema — never (rich results retired Sept 2023)
  ✗ anthropic-ai / claude-web in robots.txt — retired July 2024
  ⚠ G2 / Capterra aggregate < 4.0 — Critical (ChatGPT competitive filter)
  ⚠ JavaScript-only sites — Critical (AI crawlers don't execute JS)

WHERE TO START
  • New audit:        /geo audit https://your-site.com
  • Already audited:  /geo plan https://your-site.com
  • Just one fix:     /geo verify <technique> https://your-site.com

LEARN MORE
  • Scoring rubric:    references/scoring-rubric.md
  • Platforms guide:   references/platforms-2026.md
  • CITABLE framework: references/citable-framework.md
  • Reddit playbook:   references/reddit-strategy.md
  • SEO compat map:    references/compatibility-with-seo.md

Built by Digital Vlad — https://vdigital.app/
```

After printing the briefing, **always** ask the user one short follow-up:
"Where would you like to start? Paste a URL for `/geo audit`, or name a
sub-command from the list."

Use this same output for the empty invocation (`/geo`) and `/geo --help`.

## Orchestration Logic

### When the user invokes `/geo audit <url>`

1. **Detect business type** from homepage signals — same heuristics as `claude-seo`:
   - SaaS: pricing page, /features, /docs, "free trial"
   - E-commerce: /products, /collections, /cart, product schema
   - Publisher: /blog, /articles, article schema, author pages
   - Local: phone, address, service area, Maps embed
   - Agency: /case-studies, /portfolio, client logos
2. **Spawn sub-agents in parallel**:
   - `geo-technical` (robots.txt, llms.txt, SSR, AI crawler access)
   - `geo-content` (CITABLE scoring, passage lengths, tables/lists ratio)
   - `geo-schema` (JSON-LD Organization, knowsAbout, sameAs, FAQPage, Product)
   - `geo-presence` (questionnaire + automated off-site checks)
3. **Run verifier scripts** (real checks, not hypothetical). Always invoke
   via the `${CLAUDE_PLUGIN_ROOT}` env var so the plugin works from any cwd:
   - `python ${CLAUDE_PLUGIN_ROOT}/scripts/check_robots_txt.py <url>`
   - `python ${CLAUDE_PLUGIN_ROOT}/scripts/check_llms_txt.py <url>`
   - `python ${CLAUDE_PLUGIN_ROOT}/scripts/check_schema.py <url>`
   - `python ${CLAUDE_PLUGIN_ROOT}/scripts/check_content_structure.py <url>`
4. **Aggregate** results into a single GEO Score (0–100) using the rubric in
   `references/scoring-rubric.md`.
5. **Generate reports** via `geo-report` sub-skill: Markdown + HTML deck + HTML guide.
6. **Append author footer** (see "Author Footer" below).

### When the user invokes a specific sub-command

Load the relevant sub-skill directly. Each sub-skill is self-contained, but may
call `geo-report` at the end if the user wants an artifact.

### Co-existence with claude-seo

`claude-seo` ships a lightweight `/seo geo` command. `claude-geo` is the deep
specialist. The two are complementary:

| Use case | Use |
|----------|-----|
| Quick single-pass GEO check inside a full SEO audit | `/seo geo <url>` (claude-seo) |
| Deep GEO audit with real verification, creative plan, dual-HTML reports | `/geo audit <url>` (this skill) |
| Verifying a specific GEO technique was applied | `/geo verify <technique> <url>` |
| Strategic 90-day GEO plan including off-site/Reddit | `/geo plan <brand>` |

This skill **never** modifies `claude-seo` outputs. It runs in its own command
namespace.

## Scoring Model

A GEO Score is a weighted average across five pillars. See
`references/scoring-rubric.md` for full detail. Summary:

| Pillar | Weight | What it covers |
|--------|--------|----------------|
| Technical accessibility | 20% | robots.txt for AI bots, SSR vs JS-only, llms.txt, Cloudflare crawl-control |
| Content citability | 25% | CITABLE/BLUF, tables, lists, sentence length, front-loading, passage length 50-150 words |
| Schema & entities | 15% | JSON-LD Organization (knowsAbout, sameAs), Product/Service, FAQPage, entity chain |
| Off-site presence | 25% | Wikipedia/Wikidata, Reddit organic, G2/Capterra rating ≥4.0, YouTube, PR coverage |
| Real-world citations | 15% | Verified mentions in ChatGPT, Claude, Perplexity answers for target queries |

## Quality Gates

Hard rules enforced by every sub-skill:

- **Never recommend HowTo schema** (rich results deprecated September 2023).
- **FAQPage schema** — recommend for AI extraction (3.2x more likely to appear in
  Google AI Overviews) but explicitly note rich results were deprecated May 7,
  2026. Don't claim Google rich results benefit.
- **Never recommend `anthropic-ai` or `claude-web`** in robots.txt — both retired
  July 2024. Use the three-bot framework: `ClaudeBot`, `Claude-User`,
  `Claude-SearchBot`.
- **Aggregate review score <4.0** on G2/Capterra/Trustpilot is a HARD BLOCKER for
  ChatGPT visibility in competitive queries. Always flag as Critical.
- **JavaScript-only content** is invisible to most AI crawlers. Always flag as
  Critical.
- **Don't claim llms.txt drives Google ranking** — Google has publicly stated
  they don't use it. Recommend only for: (a) developer-tool products (IDE agents
  consume it), (b) MCP/agent-facing documentation.

## Reference Files

Load on-demand, not at startup:

- `references/geo-research-2026.md` — full GEO research base (May 2026), platform state, statistics, tactic effect sizes
- `references/platforms-2026.md` — per-platform optimization guide (ChatGPT, Claude, Perplexity, Google AIO, AI Mode, Copilot)
- `references/citable-framework.md` — CITABLE in detail with examples
- `references/scoring-rubric.md` — full scoring algorithm and thresholds
- `references/creative-techniques.md` — non-technical GEO techniques (Reddit, PR, YouTube, Wikipedia strategy)
- `references/reddit-strategy.md` — Reddit deep dive with the 6-step organic playbook
- `references/compatibility-with-seo.md` — explicit map of how this skill differs from and complements claude-seo
- `references/author.md` — author footer template (Digital Vlad / vdigital.app / Telegram / YouTube)

## Author Footer

After completing a **major deliverable** (full audit, plan, report) append the
contents of `references/author.md` as the very last block of output. Skip for
quick checks (single verifier calls, intake questions, error messages).

## Error Handling

| Scenario | Action |
|----------|--------|
| URL unreachable | Report exactly. Do not invent content. Suggest verification. |
| robots.txt missing | Note explicitly. Do not assume default-allow. |
| Site is JavaScript-only (empty raw HTML) | Hard-flag as Critical for GEO — AI crawlers do not execute JS. Recommend SSR/prerender. |
| Schema JSON-LD malformed | Report exactly which @type and which property. Provide ready-to-paste fix. |
| LLM mention verification API unavailable | Fall back to WebSearch with query templates. Mark results as "indirect signal". |
