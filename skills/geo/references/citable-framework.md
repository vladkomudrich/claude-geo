# CITABLE Framework (Discovered Labs)

The CITABLE framework reports +340% AI citations within 90 days when fully
applied. Each letter is a content-engineering requirement.

## C — Clear entity structure (BLUF)

Every page starts with a **Bottom Line Up Front** — 100-150 words directly
under the H1 that state:

- What the product / topic is (one factual sentence).
- Who it's for.
- The single sharpest differentiator.
- One concrete number (price, scale, benchmark).

**Anti-pattern:** Hero copy that's marketing prose ("Reimagining the future
of...") with the answer buried under the fold.

**Verifier hint:** `check_content_structure.py` flags pages where the first
visible paragraph doesn't contain a noun phrase matching the page topic.

## I — Intent architecture

Every H2 is phrased as a question. The first sentence immediately under each
H2 is a direct answer in 1-2 sentences. Supporting detail comes after.

**Example:**
```
## How does X handle authentication?
X uses OAuth 2.0 with PKCE. Tokens expire after 1 hour; refresh tokens
last 30 days. Configuration is in `auth.config.json`.

[supporting paragraphs here]
```

**Anti-pattern:** H2s like "Authentication", followed by 4 paragraphs of
context before the answer appears.

## T — Third-party validation

Each platform values different third-party signals:

- **ChatGPT**: Wikipedia for entity recognition; G2/Capterra ≥4.0 for product queries.
- **Perplexity**: Reddit organic mentions, fresh reviews.
- **Google AI Overviews / AI Mode**: structured data + entity knowledge graph (Wikidata, Wikipedia).
- **Claude**: peer-reviewed and primary-source citations.

Pages should link out to or reference at least 2-3 independent authoritative
sources per major claim.

## A — Answer grounding (data)

Every claim has a number. Replace qualitative language with quantified language:

| Before | After |
|--------|-------|
| "We're fast" | "Median response time 87ms across 99th percentile" |
| "Lots of users" | "2,340 active teams as of May 2026" |
| "Great support" | "Average first response: 3 minutes 24 hours/day" |

**Verifier hint:** Pages with ≥1 number per 200 words score higher.

## B — Block structure for RAG

Content is broken into **answer capsules** of 50-150 words (sweet spot
~130-160). Each capsule:

- Has a clear topic sentence.
- Can be quoted without surrounding context.
- Ends cleanly (no "as we'll see in the next section").

This matches how RAG systems chunk content (typical chunk size 256-512 tokens
with recursive splitting).

## L — Latest timestamps

Pages display a visible "Last Updated: [date]" string. Updates ≥ once every
12 months minimum, ideally every 3-6 months for evergreen content. Sites
that go >3 months without updates have **3x higher risk** of losing AI
visibility.

The `dateModified` property in JSON-LD must match the visible date.

## E — Entity schema

Required JSON-LD elements on cornerstone pages:

- `Organization` with `knowsAbout` (3+ topics) and `sameAs` (Wikipedia,
  LinkedIn, GitHub, X/Twitter).
- `Product` / `SoftwareApplication` / `Service` linked back to the
  Organization via `manufacturer` / `provider`.
- `Person` (author) with `sameAs` for long-form content.
- `FAQPage` for AI extraction (note: Google rich results deprecated May 2026,
  but ChatGPT/Perplexity/Gemini still extract from this schema).

**Entity-chain depth** is more important than schema-type count: a connected
chain (Product → Organization → Founder → Person) outperforms 10 disconnected
@types.

## CITABLE Score Computation

A page CITABLE score is the sum of seven sub-scores, each 0-100, averaged.
`check_content_structure.py` and `check_schema.py` populate the values.
Pages averaging ≥ 70 are considered well-optimized.

| Letter | Pass threshold |
|--------|----------------|
| C — BLUF | 1st paragraph contains topic noun phrase + 1 number |
| I — Intent | ≥ 70% of H2s phrased as questions OR with direct answers underneath |
| T — Third-party | ≥ 2 outbound links to authoritative sources |
| A — Answer grounding | ≥ 1 number per 200 words |
| B — Block structure | ≥ 50% of content in 50-150-word passages |
| L — Latest | Visible date within last 6 months + matching `dateModified` |
| E — Entity | Org schema with knowsAbout + sameAs + at least one product/service |
