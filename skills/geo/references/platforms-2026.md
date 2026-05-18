# Platform-Specific Optimization (May 2026)

Each AI engine weighs signals differently. Optimizing for one is not the same
as optimizing for another. Below is the consolidated platform map.

## Google — Gemini 3 + AI Mode + AI Overviews

**Scale (May 2026):**
- AI Overviews appear in **48% of all Google queries**, +58% since Dec 2025.
- AI Mode: **75M daily active users**, 1B+ queries/month (US + India), 53 additional languages.
- **93%** of AI Mode interactions are zero-click. AIO is 43% zero-click.
- Brands cited in AI Overviews see **+120% organic clicks per impression**.

**What it weighs (post Nov 2025 Gemini 3 rollout):**
- **Entity authority** (knowsAbout, Wikidata presence).
- **Factual accuracy scores** (verifiable claims).
- **Structured content quality** (semantic HTML, schema chain depth).
- Distributes citations across multiple domains in a single answer.

**Optimization focus:**
- `Organization.knowsAbout` array.
- Wikipedia / Wikidata entry.
- Structured comparison content.
- EEAT signals (author Person schema with `sameAs`).
- Personal Intelligence: AI Mode pulls Gmail/Drive context — content surfaced via Workspace integration is also factor.

## OpenAI / ChatGPT

**Scale:** ~800M weekly active users (industry estimate, not OpenAI-confirmed).

**What changed in 2025-2026:**
- **Reddit citation share fell from 60% → 10% over 6 weeks** late 2025 after parameter shifts. Slot taken by PR Newswire, Forbes, Medium.
- **Own product page citations rose 55% → 63%.**
- **Citation density** (cites/answer for brand queries) dipped from 4.95 → 2.96 (Jan-Mar 2026), now recovered to ~4.5.
- **GPT-5.5 Instant** rolled out spring 2026 with 52.5% fewer hallucinations on high-stakes prompts.
- **ChatGPT Atlas browser** launched 21 Oct 2025 on macOS.
- **OAI-SearchBot now generates more crawl events than GPTBot** (training → search shift).

**Citation source mix (early 2026):**
- Own brand pages: 63%
- Wikipedia: 26-48% top-10 share
- G2 / Capterra (rating ≥ 4.0 only): high in product queries
- PR Newswire, Forbes, Medium: rising

**Optimization focus:**
- Own product page must be primary source-of-truth (clear, factual, dated).
- Wikipedia presence (brands with Wikipedia: first cite in 28 days vs 52 without).
- G2 / Capterra aggregate ≥ 4.0 — below this is a **hard filter**.
- FAQ on-page (FAQPage schema for extraction).

## Perplexity

**Comet browser timeline:** Mac/Win 9 Jul 2025, worldwide free 2 Oct 2025, iOS 27 Mar 2026.

**Samsung Galaxy S26**: Perplexity API powers Bixby; Samsung Browser uses Perplexity APIs with agentic Comet capabilities.

**Reddit lawsuit October 2025** caused Reddit citation drop of -86% almost
immediately. By January 2026 partly recovered to 24% of all Perplexity
citations. YouTube absorbed much of the lost share.

**What it weighs:**
- **Freshness** (citing community-discussed news within days).
- **Community validation** (Reddit + YouTube comments + product forums).
- **Structured comparison content** ("X vs Y" pages).
- **Video content** rising rapidly post-lawsuit.

**Optimization focus:**
- Reddit organic presence (still 24% citation share).
- YouTube channel with category videos.
- "Best X" / "X vs Y" comparison pages.
- Fresh weekly updates.

## Anthropic / Claude

**Three-bot framework (formalized in 2026):**

| Bot | Purpose | robots.txt directive |
|-----|---------|---------------------|
| `ClaudeBot` | Training | `User-agent: ClaudeBot` |
| `Claude-User` | User-initiated fetches | `User-agent: Claude-User` |
| `Claude-SearchBot` | Search index | `User-agent: Claude-SearchBot` |

**Retired (do NOT add to robots.txt):** `anthropic-ai`, `claude-web` (retired
July 2024).

**What Claude prefers:**
- Primary sources, peer-reviewed citations.
- Nuanced, well-attributed content.
- Academic tone, accuracy.
- First-party documentation.

**Optimization focus:**
- High-quality first-party docs.
- Primary-source citations with full attribution.
- Person schema for authors with credentials.

## Microsoft Copilot

**What it weighs:**
- Bing index health.
- Schema markup (Microsoft historically leans hardest on structured data).
- LinkedIn / Microsoft ecosystem mentions.

**Optimization focus:**
- Bing-friendly schema.
- LinkedIn company page activity.
- IndexNow protocol for fast re-indexing.

## Comparison Matrix

| Engine | Reddit | Wikipedia | G2 ≥4.0 | YouTube | Own docs | Comparison pages | Schema depth |
|--------|--------|-----------|---------|---------|----------|------------------|--------------|
| ChatGPT | medium (rebalanced) | HIGH | HIGH (gate) | medium | HIGH | medium | medium |
| Perplexity | HIGH | medium | medium | HIGH | medium | HIGH | medium |
| Google AIO | low | HIGH | medium | medium | medium | medium | HIGH |
| AI Mode | low | HIGH | medium | medium | medium | medium | VERY HIGH |
| Claude | low | medium | medium | low | HIGH | medium | medium |
| Copilot | low | medium | medium | low | medium | medium | VERY HIGH |

## Agentic Commerce Protocol (ACP) — New Channel

ACP is the open standard (Apache 2.0) for AI-driven purchasing. Maintained by
OpenAI + Stripe (Meta listed as co-creator in Stripe blog; GitHub maintainers
= OpenAI + Stripe).

**Launched:** 29 Sept 2025. Status: **beta**.

**Mechanism:** Delegate Payment (spec) / Shared Payment Token (Stripe impl).
The merchant remains merchant of record; the agent (ChatGPT) buys on behalf
of the user.

**Adoption at launch:**
- Etsy US sellers: LIVE.
- Shopify (1M+ merchants): "coming soon" per Stripe blog.

**Implications for e-commerce GEO:**
- Product cards become AI-facing UI. Need structured Product schema with all
  attributes, not marketing copy.
- "Contact for pricing" = invisible to AI shopping. Must be machine-readable.
- Aggregate ratings ≥ 4.0 are the floor.
