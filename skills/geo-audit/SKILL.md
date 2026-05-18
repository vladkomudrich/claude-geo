---
name: geo-audit
description: >
  Run a full GEO audit on a target URL or brand. Orchestrates the technical,
  content, schema, and presence sub-skills in parallel; runs all verifier
  scripts; produces a single GEO Score (0-100) with five pillar breakdown
  and prioritized action plan. The audit output feeds directly into
  geo-report for MD + dual-HTML deliverables.
user-invokable: true
argument-hint: "<url>"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# Full GEO Audit

**Invocation:** `/geo audit <url>`

## Workflow

### Phase 1 — Intake (1-2 minutes)

1. Fetch homepage and a representative sample (3-5 pages: home, pricing/product,
   one blog post, one comparison page if exists, one help/docs page).
2. **Detect business type** from homepage signals (SaaS, e-commerce, publisher,
   local, agency) — same heuristics as `claude-seo` orchestrator.
3. **Extract brand name** from `<title>`, Organization schema, or homepage H1.
4. **Quick failure check:** if `<body>` of raw HTML is empty (JS-only site),
   warn the user immediately — most AI crawlers will see nothing. Continue
   audit but cap technical pillar at 40.

### Phase 2 — Parallel sub-agent dispatch

Delegate to four sub-agents in parallel:

| Sub-agent | Owns | Reads from |
|-----------|------|-----------|
| `geo-technical` | robots.txt, llms.txt, SSR check, AI crawler access | `scripts/check_robots_txt.py`, `scripts/check_llms_txt.py`, `scripts/fetch_page.py` |
| `geo-content` | CITABLE scoring, passage analysis, tables/lists/sentence-length | `scripts/check_content_structure.py` |
| `geo-schema` | JSON-LD detection, validation, knowsAbout/sameAs check | `scripts/check_schema.py` |
| `geo-presence` | Wikipedia, G2/Capterra, Reddit, YouTube, mentions interview | `scripts/check_wikipedia.py`, `scripts/check_trust_sites.py`, `scripts/check_reddit_presence.py`, `scripts/check_youtube_presence.py` |

### Phase 3 — Real-mention verification (optional but recommended)

If the user provides 3-5 **intent queries** for their category (e.g. "best
project management tool", "X vs Asana", "how to manage remote teams"),
dispatch `geo-mentions` to verify whether the brand actually appears in:

- ChatGPT (via WebSearch proxy or direct API if `OPENAI_API_KEY` set)
- Perplexity (via WebSearch proxy or direct API if `PERPLEXITY_API_KEY` set)
- Google AI Overviews (via WebSearch with `site:` operators)
- Claude (via direct API if `ANTHROPIC_API_KEY` set; else skip)

If no queries provided, generate 5 candidate queries from the business-type
detection and ask the user to confirm or edit.

### Phase 4 — Scoring

1. Each sub-agent returns a pillar score 0-100 (see `scoring-rubric.md`).
2. Compute weighted total: tech 20% + content 25% + schema 15% + presence 25%
   + mentions 15%.
3. Map to grade A/B/C/D/F.
4. Identify the **top 5 actions** by `(score_delta / effort)` ratio.
5. List **critical failures** explicitly at the top.

### Phase 5 — Report generation

Call `geo-report` sub-skill with `type=all` to produce:
- `GEO-Audit-{brand}-{YYYY-MM-DD}.md`
- `GEO-Guide-{brand}-{YYYY-MM-DD}.html`

Both saved to the user's working directory.

### Phase 6 — Author footer

Append the contents of `../geo/references/author.md` to the chat output and
embed it in the HTML guide.

## Asking for missing context

If any of the following is missing, ask the user via AskUserQuestion (one
question per concept, not all at once):

1. Brand name (only if not extractable from page).
2. Category / competitors (for intent-query generation).
3. Whether to run real LLM mention checks (cost / time implication).
4. Whether the user already has Wikipedia / G2 / Capterra listings (avoids
   redundant external searches).

## Output structure

```
# GEO Audit — {Brand}
**URL:** {url}
**Date:** {date}
**Score:** {total}/100 — Grade {grade}

## Pillar Breakdown
| Pillar | Score | Status |
|--------|-------|--------|
| Technical accessibility | XX/100 | [✓ / ⚠ / ✗] |
| Content citability | XX/100 | [✓ / ⚠ / ✗] |
| Schema & entities | XX/100 | [✓ / ⚠ / ✗] |
| Off-site presence | XX/100 | [✓ / ⚠ / ✗] |
| Real-world citations | XX/100 | [✓ / ⚠ / ✗] |

## Critical Failures
- ...

## Top 5 Highest-Impact Actions
1. [...] — estimated impact +X points, effort: Y hours
...

## Per-Pillar Findings
### Technical Accessibility
...

### Content Citability
...

### Schema & Entities
...

### Off-site Presence
...

### Real-world Citations
...

## Source Verification
[List which scripts ran, which external sources queried, any uncertainty notes]
```

## Quality gates

- Never claim a citation exists without a verifier-script-confirmed result.
- Mark estimates vs verified explicitly.
- If WebSearch returns no useful data for a mention check, say so — don't
  invent.
