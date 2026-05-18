---
name: geo-schema
description: >
  JSON-LD schema audit specifically for AI engines. Detects, validates,
  and generates Schema.org markup with GEO-priority properties:
  Organization.knowsAbout (#2 most important markup as of March 2026),
  Organization.sameAs (entity linking glue), Product/SoftwareApplication/
  Service, FAQPage (for AI extraction even after May 2026 rich-results
  deprecation), Person (author), and entity chain depth (Product →
  Organization → Founder → Person). Triggers on: JSON-LD, structured data,
  knowsAbout, sameAs, FAQPage for AI, entity chain, schema for AI.
user-invokable: true
argument-hint: "<url>"
license: MIT
metadata:
  author: Digital Vlad
  version: "1.0.0"
  category: geo
---

# Schema Audit for GEO

**Invocation:** `/geo schema <url>`

## What this checks

This skill is **GEO-specific**. For Google rich-results validation, defer to
`claude-seo` `/seo schema`. This skill prioritizes the properties that AI
engines use for entity authority.

### Detection

Fetch the page, extract all `<script type="application/ld+json">` blocks,
parse each.

### Required @types

| @type | Required for | Notes |
|-------|--------------|-------|
| `Organization` | Every domain | Must have `knowsAbout` (≥3 topics) and `sameAs` |
| `WebSite` | Every domain | Add `SearchAction` |
| `Product` / `SoftwareApplication` / `Service` | Product pages | Link back to Organization |
| `Article` / `BlogPosting` | Editorial content | With `author` (Person schema) |
| `Person` | Author bio pages | `sameAs` to Wikipedia/LinkedIn/GitHub |
| `BreadcrumbList` | Any deep page | Helps entity context |
| `FAQPage` | Pages with Q&A | For AI extraction only — note Google rich results deprecated 7 May 2026 |

### Key 2026 changes to enforce

1. **knowsAbout property on Organization/Person** — #2 most important markup
   element. Must list 3+ specific topics the brand has expertise in. Used by
   Gemini 3 AI Mode for source selection.
2. **sameAs identifiers** — Connect Organization + Person to:
   - Wikipedia URL
   - Wikidata URL (`https://www.wikidata.org/wiki/Q...`)
   - LinkedIn company / personal
   - GitHub org
   - X / Twitter
   - YouTube channel
   - Crunchbase profile
3. **HowTo schema** — never recommend (retired Sept 2023).
4. **FAQPage schema** — recommend with explicit caveat: rich results
   deprecated 7 May 2026 by Google, but ChatGPT/Perplexity/Gemini still
   extract from it. Pages with FAQPage are 3.2× more likely to appear in
   Google AI Overviews.
5. **Entity chain depth** — connected chains (Product → Organization →
   Founder → Person) outperform 10 disconnected @types.

### Validation rules

- `@context` present and equals `https://schema.org` (not `http://`).
- `@type` valid.
- Required properties present per @type.
- No placeholder text (`"Your Company Name"`, `"https://example.com"`).
- Dates ISO-8601 (`2026-05-18` not `5/18/2026`).
- URLs absolute, not relative.
- Number fields are numbers, not strings.

## Generation templates

When the page lacks key schema, generate ready-to-paste JSON-LD. Example:

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{Brand}",
  "url": "{site}",
  "description": "{1-2 sentence factual description}",
  "knowsAbout": [
    "{specific topic 1}",
    "{specific topic 2}",
    "{specific topic 3}"
  ],
  "sameAs": [
    "{wikipedia URL if exists}",
    "{wikidata URL if exists}",
    "{linkedin URL}",
    "{github URL}",
    "{x.com URL}",
    "{youtube URL}",
    "{crunchbase URL}"
  ],
  "founder": {
    "@type": "Person",
    "name": "{founder name}",
    "sameAs": ["{linkedin}", "{wikipedia}"]
  }
}
```

## Verifier script

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/check_schema.py <url>
```

Outputs a structured report listing every @type found, every missing required
property, and a score 0-100 per the rubric.

## Output

```
# Schema Audit (GEO) — {url}

## Pillar Score: XX/100

## Schemas detected
- Organization (has knowsAbout: yes/no; sameAs count: N)
- WebSite ...
- Product ...
- FAQPage (caveat: AI-only signal post-May-2026)

## Gaps
- Missing Organization.knowsAbout — generate suggested array
- Missing Person schema on author pages
- Entity chain: standalone Organization, no Product link-back

## Generated JSON-LD (ready to paste)
```json
{
  ...
}
```

## Top Actions (Schema pillar)
1. Add `knowsAbout` array on Organization — 3 topics. Highest GEO leverage.
2. Add `sameAs` array including Wikipedia / Wikidata / LinkedIn.
3. Build entity chain: Product.manufacturer → Organization.founder → Person.
```

## Quality gates

- Reject `HowTo` schema everywhere (deprecated Sept 2023).
- For FAQPage, explicitly note "rich results deprecated, schema kept for AI
  extraction".
- Don't claim schema alone "boosts" rankings — Ahrefs 1885-page study showed
  no isolated effect.
- Always validate against schema.org @context, not custom contexts.
