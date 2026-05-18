---
name: geo-verify
description: >
  Verify that a specific GEO technique was actually applied on a target
  URL or brand. Each technique has a dedicated verifier script that
  performs real checks (not hypothetical scoring). Use after implementing
  changes from an audit or plan to confirm the change landed. Triggers on:
  verify, check that, did I apply, was the change deployed, recheck.
user-invokable: true
argument-hint: "<technique> <url|brand>"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# Technique Verification Dispatcher

**Invocation:** `/geo verify <technique> <url|brand>`

This sub-skill is the verification surface of the plugin. Each technique maps
to a verifier script that performs **a real check**, not a hypothetical score.

## Available techniques

| Technique | Verifier script | What it confirms |
|-----------|----------------|------------------|
| `robots-txt` | `check_robots_txt.py` | Each major AI bot has explicit Allow / fallback |
| `robots-txt-claude` | `check_robots_txt.py --bots=claude` | Three-bot Anthropic framework configured |
| `robots-txt-openai` | `check_robots_txt.py --bots=openai` | GPTBot + OAI-SearchBot + ChatGPT-User configured |
| `llms-txt` | `check_llms_txt.py` | `/llms.txt` present and structurally valid |
| `ssr` | `fetch_page.py --check-ssr` | Raw HTML body has real content (not JS-only) |
| `schema-organization` | `check_schema.py --type=Organization` | Organization JSON-LD present and valid |
| `schema-knowsabout` | `check_schema.py --property=knowsAbout` | `knowsAbout` array with ≥3 topics present |
| `schema-sameas` | `check_schema.py --property=sameAs` | `sameAs` linking to Wikipedia/LinkedIn/etc. |
| `schema-faqpage` | `check_schema.py --type=FAQPage` | FAQPage schema (AI extraction signal) |
| `schema-product` | `check_schema.py --type=Product` | Product schema linked to Organization |
| `schema-entity-chain` | `check_schema.py --chain` | Product → Org → Founder → Person chain present |
| `content-bluf` | `check_content_structure.py --check=bluf` | BLUF in first 60 words below H1 |
| `content-tables` | `check_content_structure.py --check=tables` | ≥1 table (≥3 for max) on the page |
| `content-lists` | `check_content_structure.py --check=lists` | ≥1 list with ≥5 items |
| `content-sentence-length` | `check_content_structure.py --check=sentences` | Avg sentence length ≤ 10 words |
| `content-front-loading` | `check_content_structure.py --check=frontload` | Key stats in first third of page |
| `content-passage-length` | `check_content_structure.py --check=passages` | Passages 50-150 words present |
| `content-last-updated` | `check_content_structure.py --check=date` | Visible date string + dateModified match |
| `wikipedia` | `check_wikipedia.py` | Wikipedia article and/or Wikidata Q-item exist |
| `g2-rating` | `check_trust_sites.py --site=g2` | G2 listing present with rating ≥ 4.0 |
| `capterra-rating` | `check_trust_sites.py --site=capterra` | Capterra rating ≥ 4.0 |
| `trustpilot-rating` | `check_trust_sites.py --site=trustpilot` | Trustpilot rating ≥ 4.0 |
| `reddit-presence` | `check_reddit_presence.py` | ≥10 organic mentions in last 90 days |
| `youtube-presence` | `check_youtube_presence.py` | ≥1 third-party video mentioning brand |
| `llm-mention-chatgpt` | `check_llm_mentions.py --engine=chatgpt` | Brand cited in ChatGPT for category queries |
| `llm-mention-perplexity` | `check_llm_mentions.py --engine=perplexity` | Brand cited in Perplexity |
| `llm-mention-aio` | `check_llm_mentions.py --engine=aio` | Brand cited in Google AI Overviews |
| `llm-mention-claude` | `check_llm_mentions.py --engine=claude` | Brand cited in Claude |

## Workflow

1. Parse `<technique>` argument.
2. If unknown, list available techniques.
3. Resolve to script path and arguments.
4. Run the script.
5. Render structured output: PASS / FAIL / PARTIAL with the captured evidence.

## Output

```
# Verification — {technique}
**Target:** {url|brand}
**Result:** PASS / FAIL / PARTIAL

## Evidence
{raw script output, formatted}

## Recommendation
{if FAIL or PARTIAL: specific next step}
{if PASS: confirm and suggest next adjacent technique}
```

## Multi-technique batch

If the user calls `/geo verify all <url>`, run the technical batch:
- `robots-txt`
- `llms-txt`
- `ssr`
- `schema-organization`
- `schema-knowsabout`
- `schema-sameas`
- `content-bluf`
- `content-tables`
- `content-front-loading`

For off-site batch: `/geo verify presence <brand>`:
- `wikipedia`
- `g2-rating`
- `capterra-rating`
- `trustpilot-rating`
- `reddit-presence`
- `youtube-presence`

## Quality gates

- Verifier scripts must not invent results. If a check cannot complete (DNS
  failure, rate limit, API error), report ERROR with the underlying cause.
- PARTIAL = partial success (e.g. schema present but missing one required
  property). Always list what's present vs. what's missing.
- Never claim a brand is cited by an LLM without the raw quoted sentence.
