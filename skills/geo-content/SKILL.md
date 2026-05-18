---
name: geo-content
description: >
  Content structure audit for GEO. Scores against the CITABLE framework
  (Clear-entity-BLUF, Intent architecture, Third-party validation, Answer
  grounding, Block structure, Latest timestamps, Entity schema). Counts
  tables, lists, average sentence length, passage lengths, front-loaded
  facts. Identifies the specific passages and headings that need rewriting
  to lift AI citation likelihood. Triggers on: CITABLE, BLUF, content
  structure, passage length, answer blocks, AI citation content.
user-invokable: true
argument-hint: "<url>"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# Content Citability Audit

**Invocation:** `/geo content <url>`

## What this checks

The CITABLE framework — see `../geo/references/citable-framework.md` for full
detail. This skill scores each letter and produces concrete rewriting
suggestions.

### Mechanical checks (run via script)

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_content_structure.py <url>
```

The script extracts and reports:
- Table count.
- Ordered/unordered list count + items per list.
- Average sentence length across the page body.
- Median paragraph length in words.
- Passage segmentation (50-150 word self-contained blocks).
- Position of first numeric statistic (which third of the page).
- Visible date string (Last Updated / Published).
- Heading hierarchy (H1 count, H2/H3 ratio).
- Question-style H2/H3 count (heuristic: ends with `?` or starts with
  who/what/when/why/how).

### Conceptual checks (Claude reads the content)

For each cornerstone page:

1. **BLUF check**: Does the first paragraph (within 60 words of H1) answer
   "what is this and what's the differentiator"?
2. **Intent check**: For each H2, is the first sentence below it a direct
   answer to an implicit question?
3. **Third-party check**: Are there ≥ 2 outbound links to authoritative
   sources per major claim?
4. **Answer grounding**: Identify hand-wavy claims ("fast", "lots of",
   "great") and propose quantified rewrites.
5. **Block structure**: Identify the longest passage. If > 200 words without
   structure, recommend splitting.
6. **Latest**: Is there a visible date? Does it match `dateModified` in
   JSON-LD?

## Output

```
# Content Citability — {url}

## Pillar Score: XX/100

## CITABLE Breakdown
| Letter | Status | Score | Notes |
|--------|--------|-------|-------|
| C — BLUF | ✓ / ⚠ / ✗ | XX | ... |
| I — Intent | ✓ / ⚠ / ✗ | XX | ... |
| T — Third-party | ✓ / ⚠ / ✗ | XX | ... |
| A — Answer grounding | ✓ / ⚠ / ✗ | XX | ... |
| B — Block structure | ✓ / ⚠ / ✗ | XX | ... |
| L — Latest | ✓ / ⚠ / ✗ | XX | ... |
| E — Entity (deferred to geo-schema) | n/a | n/a | see schema audit |

## Mechanical Metrics
- Tables: N (target: ≥ 1 on comparison pages, ≥ 3 ideal)
- Lists: N (target: ≥ 8 list sections for max impact)
- Avg sentence length: N words (target: ≤ 10)
- Front-loading: first numeric stat at X% of page (target: ≤ 33%)
- Self-contained 50-150 word passages: N / total content
- Visible date: present / missing
- Page length: X words / Y chars

## Specific Rewrite Suggestions
1. Section "[H2 title]" — first paragraph buries the answer. Recommended:
   "[concrete one-line rewrite]"
2. "[H2 title]" — replace "[hand-wavy phrase]" with "[quantified version using
   data from the page]"
3. ...

## Top Actions (Content pillar)
1. Convert prose at [section] into a 5-7 row table. Extraction rate jumps
   from ~23% to ~81%.
2. ...
```

## Quality gates

- Never suggest keyword stuffing (~0% effect on LLMs).
- Don't recommend shortening below 1500 words on cornerstone pages — long
  pages get more citations (10.18 vs 2.39 for short pages).
- Front-loading is the highest-leverage cheap fix — call it out by name.
