---
name: geo-mentions
description: >
  Verify real brand mentions in AI engine answers. Runs a curated set of
  category intent queries against ChatGPT, Claude, Perplexity, and Google
  AI Overviews (or their WebSearch proxies) and reports whether the brand
  appears in answers, whether the description is correct, and whether the
  sentiment is positive/neutral/negative. This is the only Pillar 5 ground
  truth — everything else is signal proxying. Triggers on: brand mentions,
  AI citations, LLM mention check, does ChatGPT cite my brand, Perplexity
  cites, AI visibility.
user-invokable: true
argument-hint: "<brand> [--queries=q1,q2,q3]"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# Real LLM Mention Verification

**Invocation:** `/geo mentions <brand>` (optionally `--queries=q1,q2,q3`)

This is the **only** sub-skill that produces Pillar 5 (Real-world citations)
scoring data. Everything else is signal proxying.

## Step 1 — Determine queries

If the user provides `--queries`, use those. Otherwise, generate 5 candidate
**intent queries** from category + competitor data, then ask the user to
confirm or edit.

**Intent-query patterns:**
1. `"best [category] in 2026"`
2. `"[brand] vs [competitor]"`
3. `"how to [task that brand solves]"`
4. `"[category] for [audience segment]"`
5. `"is [brand] worth it"` OR `"[brand] review"`

## Step 2 — Run checks

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_llm_mentions.py <brand> --queries=q1,q2,q3
```

The script attempts each engine in this order, falling back if API keys are
missing:

| Engine | If API key present | Fallback |
|--------|-------------------|----------|
| ChatGPT | OpenAI API (`OPENAI_API_KEY`) with web-search-enabled assistant | WebSearch with `site:chat.openai.com` + curated logged Q&A patterns; mark as **indirect** |
| Claude | Anthropic API (`ANTHROPIC_API_KEY`) | Skip (no public Claude search proxy) |
| Perplexity | Perplexity API (`PERPLEXITY_API_KEY`) | WebSearch with `site:perplexity.ai` |
| Google AI Overviews | DataForSEO MCP if available | WebSearch with the query; check for AIO marker |

**Each result** captures:
- Engine name.
- Query.
- Whether brand mentioned.
- The actual sentence/passage mentioning the brand.
- Sentiment (Claude classifies: positive / neutral / negative).
- Factual accuracy (Claude flags: accurate / partially-accurate / inaccurate).

## Step 3 — Score

Per `references/scoring-rubric.md`:

- Brand cited by ChatGPT for ≥1 of 5 queries: +20 (≥3: +30 instead).
- Brand cited by Perplexity for ≥1: +15 (≥3: +25 instead).
- Brand cited by Google AI Overviews for ≥1: +15.
- Brand cited by Claude for ≥1: +10.
- Description factually correct: +10.
- Sentiment neutral or positive: +10.

Cap at 100.

## Step 4 — Output

```
# LLM Mention Check — {brand}

## Pillar 5 Score: XX/100

## Per-engine results

### ChatGPT (X/5 queries cite brand)
| Query | Cited | Description | Sentiment | Accuracy |
|-------|-------|-------------|-----------|----------|
| "best [cat] in 2026" | YES | "{exact sentence}" | positive | accurate |
| "..." | NO | — | — | — |

### Claude (X/5)
...

### Perplexity (X/5)
...

### Google AI Overviews (X/5)
...

## Findings
- Strongest engine: {name} ({X}/5)
- Weakest engine: {name} ({Y}/5)
- Common reason for non-citation (where identifiable): [...]

## Recommended remediation
For each missing engine, recommend specific actions from the broader audit:
- ChatGPT non-citation when G2 <4.0 → Top priority: G2 rating recovery.
- Perplexity non-citation when no Reddit / YouTube → Top priority: Reddit
  cadence + YouTube channel.
- Google AIO non-citation when no Wikipedia → Top priority: Wikipedia draft.
```

## Quality gates

- Never claim a citation exists without the raw sentence captured.
- Mark indirect (WebSearch proxy) results as such.
- If all engines return zero citations, that's a result — report it as the
  starting point. Do NOT manufacture a "soft" signal.

## API key handling

The script reads environment variables. If a key is missing, the script
proceeds with WebSearch fallback and tags results accordingly. Never log keys.
