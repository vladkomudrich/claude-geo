---
name: geo-plan
description: >
  Strategic 90-day GEO roadmap. Combines findings from technical, content,
  schema, and presence audits with the user's stated existing footprint
  to produce a sequenced plan: week-by-week actions, owners, expected
  score deltas, and verification checkpoints. Includes both technical
  fixes (robots.txt, schema, content rewrites) and creative work (Reddit
  cadence, Wikipedia draft, G2 review campaign, YouTube launch, PR).
  Triggers on: GEO plan, GEO roadmap, 90-day plan, strategy, what should
  I do first, GEO priorities.
user-invokable: true
argument-hint: "<brand|url>"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# Strategic GEO Roadmap

**Invocation:** `/geo plan <brand|url>`

This sub-skill produces a sequenced 90-day plan. It can run **after** a full
audit (`/geo audit`) and use those findings, or **standalone** with an
intake interview.

## Phase 1 — Inputs

If a recent `/geo audit` output exists in the workspace
(`GEO-Audit-{brand}-{date}.md` within last 14 days), load it. Otherwise, ask
the user via AskUserQuestion:

1. URL + brand name.
2. Whether they want a tech-heavy plan, creative-heavy plan, or balanced.
3. Estimated weekly effort available (1-5 hrs / 5-15 hrs / 15+ hrs).
4. Whether the user has budget for PR / paid review-campaign tools.

## Phase 2 — Plan structure

The plan is organized in three rolling 30-day blocks. Within each block,
actions are tagged:

- **[FOUNDATION]** — must be done before other actions land.
- **[TECHNICAL]** — engineer / developer time.
- **[CONTENT]** — writer / marketing time.
- **[CREATIVE]** — founder / community time (Reddit, PR, Wikipedia).
- **[VERIFY]** — checkpoint using `/geo verify ...`.

### Block 1: Foundation (Days 1-30)

Priority: stop visibility bleeding and put fundamentals in place.

| Day | Action | Tag | Expected score delta |
|-----|--------|-----|---------------------|
| 1-2 | Audit `robots.txt`: allow all major AI bots | TECHNICAL | +5-15 |
| 1-2 | Check Cloudflare AI Crawl Control if applicable | TECHNICAL | +5 |
| 3-5 | Add `Organization` JSON-LD with `knowsAbout` (3+ topics) and `sameAs` (Wikipedia/LinkedIn/GitHub/YouTube/etc.) | TECHNICAL | +10-15 |
| 3-5 | Add `Product` / `Service` schema linked to Organization | TECHNICAL | +5 |
| 7-10 | Front-load BLUF (100-150 words direct answer below H1) on top 5 pages | CONTENT | +5-10 |
| 10-14 | Convert key prose sections into tables/lists on top 5 pages | CONTENT | +5-15 |
| 14-21 | Add visible "Last Updated" date + matching `dateModified` | CONTENT | +5 |
| 14-21 | Claim G2 + Capterra + Trustpilot listings if not claimed | CREATIVE | +5-15 |
| 21-30 | Create Wikidata Q-item with all `sameAs` | CREATIVE | +10 |
| 28-30 | **VERIFY** technical pillar: `/geo verify schema-knowsabout <url>` and `/geo verify robots-txt <url>` and `/geo verify ssr <url>` | VERIFY | n/a |

### Block 2: Citation engine (Days 31-60)

Priority: build the third-party signals.

| Day | Action | Tag | Expected score delta |
|-----|--------|-----|---------------------|
| 31-45 | Reddit organic cadence: 10-15 comments/week in 2-3 target subreddits — founder account | CREATIVE | gradual +10-15 |
| 31-45 | If Wikipedia notable: draft article in user space → submit via AfC | CREATIVE | +20 over 4-12 weeks |
| 31-45 | If G2/Capterra <4.0: review-request campaign with focused remediation of common complaints | CREATIVE | +20 (removes filter) |
| 45-60 | Create 2-3 "X vs Y" comparison pages with structured tables | CONTENT | +10 |
| 45-60 | Create FAQ pages with FAQPage schema (note: for AI extraction, Google rich results deprecated) | CONTENT | +5-10 |
| 45-60 | Glossary pages for category terminology | CONTENT | +5 |
| 60 | **VERIFY** presence pillar: `/geo trust <brand>` and `/geo reddit <brand>` | VERIFY | n/a |

### Block 3: Verification + diversification (Days 61-90)

Priority: confirm the work landed in actual LLM answers and diversify.

| Day | Action | Tag | Expected score delta |
|-----|--------|-----|---------------------|
| 61-75 | YouTube channel launch: 12 short videos covering category top questions, with full transcripts in descriptions | CREATIVE | +10-15 |
| 61-75 | One PR moment: original research / survey / data study with embargo + tier-1 outreach | CREATIVE | +10 |
| 75-90 | Hacker News Show HN (if dev tool) OR Product Hunt launch | CREATIVE | +5-10 |
| 75-90 | LinkedIn company-page activation: 2-3 posts/week | CREATIVE | +5 |
| 85-90 | **VERIFY** real mentions: `/geo mentions <brand> --queries=...` against ChatGPT / Claude / Perplexity / Google AIO | VERIFY | reveals actual Pillar 5 score |
| 90 | **Full re-audit**: `/geo audit <url>` and compare to baseline. Generate progress report. | VERIFY | n/a |

## Phase 3 — Output

```
# GEO Plan — {brand}
**Baseline score:** {if from audit} XX/100, Grade {grade}
**Target after 90 days:** XX+15 to XX+30 points (depending on effort level)

## Block 1 — Foundation (Days 1-30)
{table as above, customized}

## Block 2 — Citation engine (Days 31-60)
...

## Block 3 — Verification + diversification (Days 61-90)
...

## Owner assignments (suggested)
| Action | Owner | Estimate |
|--------|-------|----------|
| robots.txt update | Engineer | 30 min |
| Organization JSON-LD | Engineer | 1 hour |
| Reddit cadence | Founder | 30 min/day |
| Wikipedia draft | Marketing / external editor | 4-8 hours |
| G2 review campaign | Marketing | 2 hours setup + ongoing |
| YouTube launch | Marketing + Founder | 40-80 hours over Block 3 |

## Risk register
- Reddit volatility: do NOT concentrate strategy on Reddit alone.
- G2 rating recovery may take longer than 30 days; start Week 1 not Week 5.
- Wikipedia AfC review can take 2-12 weeks. Submit early.
- Algorithm shifts (like ChatGPT Q4 2025 rebalance) are unpredictable.
  Monitor monthly.

## Verification checkpoints
- Day 30: technical pillar check.
- Day 60: presence pillar check.
- Day 90: full re-audit + Pillar 5 LLM mention verification.
```

## Author footer

Append `../geo/references/author.md`.

## Quality gates

- Never promise specific score outcomes — give ranges.
- Never recommend action that depends on a competitor's failure ("when X
  goes down...").
- Build diversification into every plan — never single-platform concentration.
- Verification steps are mandatory in every plan.
