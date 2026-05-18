# GEO Scoring Rubric

A GEO Score is the weighted average of five pillar scores, each on a 0-100
scale. Pillars are independent — a site can score 90 on technical and 20 on
off-site presence; the overall score reflects both.

## Pillar weights

| Pillar | Weight | Computed by |
|--------|--------|-------------|
| Technical accessibility | 20% | `scripts/check_robots_txt.py` + `scripts/check_llms_txt.py` + SSR check |
| Content citability | 25% | `scripts/check_content_structure.py` |
| Schema & entities | 15% | `scripts/check_schema.py` |
| Off-site presence | 25% | `scripts/check_wikipedia.py` + `scripts/check_trust_sites.py` + `scripts/check_reddit_presence.py` + `scripts/check_youtube_presence.py` |
| Real-world citations | 15% | `scripts/check_llm_mentions.py` |

## Pillar 1: Technical accessibility (0-100)

| Sub-signal | Points | Source |
|------------|--------|--------|
| robots.txt explicitly allows `GPTBot` OR `OAI-SearchBot` | +15 | check_robots_txt |
| robots.txt explicitly allows `ClaudeBot` AND `Claude-SearchBot` | +15 | check_robots_txt |
| robots.txt explicitly allows `PerplexityBot` AND `Perplexity-User` | +10 | check_robots_txt |
| robots.txt allows `Google-Extended` | +5 | check_robots_txt |
| `Bytespider`, `cohere-ai` decision documented either way | +5 | check_robots_txt |
| Content is server-rendered (visible in raw HTML) | +25 | fetch_page comparison |
| `/llms.txt` present and valid (developer-tool product only) | +10 | check_llms_txt |
| Cloudflare Pay-Per-Crawl: AI bots not silently blocked | +5 | check_robots_txt note |
| Sitemap fetchable | +10 | fetch_page |

**Critical failures (auto-cap pillar at 40):**
- Site is JavaScript-only with empty raw HTML.
- robots.txt blocks ALL major AI search bots.

## Pillar 2: Content citability (0-100)

Computed by `check_content_structure.py`. Each page sampled.

| Sub-signal | Points |
|------------|--------|
| Page ≥ 1 table | +10 |
| Page ≥ 3 tables | +15 (replaces +10) |
| Page ≥ 1 ordered/unordered list with ≥ 5 items | +10 |
| Page ≥ 8 list sections | +15 (replaces +10) |
| Average sentence length ≤ 12 words | +10 |
| Average sentence length ≤ 10 words | +15 (replaces +10) |
| Direct answer in first 60 words of any H2 section | +10 |
| Front-loaded structure (key facts in first 1/3 of page) | +10 |
| Self-contained passages 50-150 words present | +10 |
| Visible "Last Updated" or "Published" date | +5 |
| At least one statistic / specific number per 200 words | +10 |
| Page length ≥ 1500 words on cornerstone pages | +5 |
| Comparison-style "X vs Y" page exists with structured table | +5 |

**Bonus (any of these +5, max +15):**
- Glossary / terminology page exists.
- FAQ section with question-style H2/H3.
- Quote/citation blocks with attribution.

## Pillar 3: Schema & entities (0-100)

Computed by `check_schema.py`.

| Sub-signal | Points |
|------------|--------|
| `Organization` JSON-LD present | +15 |
| `Organization.knowsAbout` array with ≥ 3 topics | +15 |
| `Organization.sameAs` includes Wikipedia / LinkedIn / GitHub | +15 |
| `Product` / `SoftwareApplication` / `Service` schema | +10 |
| `FAQPage` schema present (mark explicitly: for AI extraction, not Google rich results) | +10 |
| `Person` (author) schema on long-form content | +5 |
| `BreadcrumbList` | +5 |
| 3+ distinct @type values on a single page | +10 |
| `WebSite` with `SearchAction` | +5 |
| Entity chain depth (Product → Organization → Person) present | +10 |

**Critical failures (auto-cap pillar at 30):**
- JSON-LD parse errors.
- `HowTo` schema in use (deprecated September 2023).

## Pillar 4: Off-site presence (0-100)

Computed by `check_wikipedia.py`, `check_trust_sites.py`,
`check_reddit_presence.py`, `check_youtube_presence.py`.

| Sub-signal | Points |
|------------|--------|
| Wikipedia article for brand | +20 |
| Wikidata entry with `sameAs` links | +10 |
| G2 listing with aggregate rating ≥ 4.0 | +15 |
| G2 listing with aggregate rating < 4.0 | -10 (penalty — ChatGPT filter blocker) |
| Capterra OR Trustpilot listing with rating ≥ 4.0 | +10 |
| Reddit: ≥ 10 organic mentions in last 90 days (non-spam) | +15 |
| Reddit: brand appears in any subreddit's recommended-tools wiki | +10 |
| YouTube: ≥ 5 third-party videos mentioning brand | +10 |
| YouTube: own brand channel with ≥ 12 videos | +5 |
| LinkedIn company page with ≥ 1000 followers | +5 |
| Recent (≤ 6 months) PR coverage on tier-1 outlet | +10 |

## Pillar 5: Real-world citations (0-100)

Computed by `check_llm_mentions.py` — actual queries to LLMs (or WebSearch
proxies) for a curated set of "intent queries" for the brand's category.

| Sub-signal | Points |
|------------|--------|
| Brand cited by ChatGPT for ≥ 1 of 5 category queries | +20 |
| Brand cited by ChatGPT for ≥ 3 of 5 category queries | +30 (replaces +20) |
| Brand cited by Perplexity for ≥ 1 of 5 | +15 |
| Brand cited by Perplexity for ≥ 3 of 5 | +25 (replaces +15) |
| Brand cited by Google AI Overviews for ≥ 1 | +15 |
| Brand cited by Claude for ≥ 1 | +10 |
| Brand description in LLM answers is factually correct | +10 |
| Brand sentiment is neutral or positive | +10 |

## Grade thresholds

| Total score | Grade | Meaning |
|-------------|-------|---------|
| 85-100 | A | Excellent GEO posture — maintain and monitor |
| 70-84 | B | Strong but with specific gaps — see top 5 actions |
| 55-69 | C | Average — measurable upside in 60-90 days |
| 40-54 | D | Significant gaps — prioritize critical findings |
| 0-39 | F | Critical — site is largely invisible to AI engines |

## Output requirements

Every audit output must include:
1. Total score with grade.
2. Per-pillar score with one-sentence rationale.
3. Top 5 highest-impact changes ranked by `(estimated_score_delta / effort)`.
4. Critical failures listed at the top with their auto-cap note.
