# Creative GEO Techniques (Non-Technical)

Technical GEO (schema, robots.txt, page structure) is necessary but not
sufficient. The **off-site / creative** layer is what makes a brand actually
appear in AI answers. This file is the playbook.

## 1. Wikipedia / Wikidata

**Why it matters:**
- Brands with a Wikipedia article get their first ChatGPT citation in
  **28 days on average**. Without Wikipedia: 52 days.
- ChatGPT pulls 26-48% of top-10 citations from Wikipedia for entity queries.
- Wikidata is the underlying graph that Google AI Mode + Gemini 3 use for
  entity authority scoring.

**Playbook:**
1. **Eligibility check.** Wikipedia notability rules require multiple
   independent reliable secondary sources. List existing tier-1 coverage
   (NYT, WSJ, TechCrunch, FT, Forbes) — if you can't cite 3-5 articles, you
   need PR first.
2. **Wikidata first.** Wikidata is more permissive. Create a Wikidata item
   for the brand + key people. Add `instance of`, `industry`, `founded`,
   `founder`, `website`, `Crunchbase ID`, `LinkedIn ID`.
3. **Draft in user space.** Do NOT publish directly. Use Wikipedia draft
   space (`User:Yourname/Brandname`) with neutral tone, citations only.
4. **AfC submission.** Submit via Articles for Creation; expect 2-12 week
   review.
5. **Maintain.** Post-publication, the article must be maintained (factual,
   neutral). Bad behavior (puffery, self-edits) causes deletion.

**Anti-patterns:** Editing your own page from the company IP. Promotional
language. Citing your own blog as a source.

## 2. Reddit (deep dive in `reddit-strategy.md`)

**Reach:** ~40% citation share across AI engines combined. 24% of Perplexity
even after the rebalance.

**Three modes that work:**
1. **Founder presence.** Founder account, real name, posts substantive
   content in 2-3 target subreddits. Not "I built X". Answer questions in
   the space, contribute to threads, build a reputation. Then link the
   product when it's the actual answer.
2. **Customer success stories.** Get real customers to write organic
   reviews in r/SaaS, r/webdev, etc. Never astroturf — it gets caught
   instantly and banned.
3. **Tool wiki entries.** Many subreddits have a sidebar wiki of recommended
   tools. Getting added (via earned recommendation) is high-leverage.

## 3. G2 / Capterra / Trustpilot

**Hard floor: aggregate score ≥ 4.0.** Below this is a **filter** that
prevents ChatGPT from citing the brand for competitive queries even when
content is excellent.

**Playbook:**
1. **Claim listings.** G2, Capterra, Trustpilot, Software Advice,
   GetApp, TrustRadius.
2. **Request reviews systematically.** Aim for 50+ reviews on G2 in first
   90 days. Tools: G2's Review Generation, in-app NPS-prompt + redirect,
   email campaigns.
3. **Respond to all reviews** (positive and negative). Response rate
   correlates with aggregate score recovery.
4. **Compare matrices.** Submit accurate "X vs Y" data to G2 — these
   pages are heavily cited.

## 4. YouTube

**Why:** Perplexity has shifted Reddit-share-loss into YouTube. ChatGPT
increasingly cites video transcripts. Google AIO surfaces YouTube clips.

**Two strands:**
1. **Own channel.** Tutorial videos, product walkthroughs, founder talks.
   Minimum 12 videos to be a "real" channel. Closed captions + transcript
   in description (transcript text is what LLMs index).
2. **Third-party mentions.** Sponsor / partner with relevant creators. Get
   listed in "best X" review videos. Mention from a creator with 50k+
   subs is high signal.

**Optimization:**
- Video title is a question matching search intent.
- Description starts with TL;DR + 3 bullet timestamps.
- Transcript explicitly mentions the brand 3-5 times in first 60 seconds.

## 5. PR & tier-1 coverage

**What replaced Reddit slots in ChatGPT** after Q4 2025 rebalance:
PR Newswire, Forbes, Medium, TechCrunch.

**Playbook:**
1. **Press release distribution.** PR Newswire ($800-1200/release) seeds the
   syndication network. Even minor releases get picked up by 30-50 sites.
2. **Founder bylines.** Get the founder bylined in Forbes Council, Inc, Fast
   Company, HBR — these get indexed and cited.
3. **Data-driven studies.** Original research with surprising numbers is
   the #1 PR magnet. Survey your customers (n>100), publish on your domain,
   pitch press.
4. **Awards.** G2 Leader badges, Capterra Shortlist, industry awards. Each
   creates a citable third-party signal.

## 6. Reddit / Hacker News / Product Hunt for tech audiences

- **Hacker News**: front page → indexed by every AI engine within hours.
  Submit timing matters (Tue-Thu, 8am ET).
- **Product Hunt**: Top 5 of the day → ~30 backlinks + creator press.
- **Indie Hackers**: founder posts about journey → quoted in startup-advice queries.

## 7. LinkedIn

Lower weight than the above, but **non-zero** for Copilot. LinkedIn presence
+ activity from the founder account creates entity-recognition signal for
the Microsoft ecosystem.

## 8. Glossary / Educational content (owned)

Glossary pages get cited **disproportionately** for definition queries
("what is X?"). Create one glossary entry per concept in your domain. 200-400
words each. Each page has its own `DefinedTerm` schema.

## 9. Original research and benchmarks

ChatGPT cites unique data **3x more often** than rehashed industry data.
Run a survey, benchmark, or longitudinal study once per quarter. Format:

- Dedicated page on your domain (`/research/[name]/`).
- 5-7 headline statistics in the first 200 words.
- Tables with the underlying data.
- Methodology section.
- PDF download (optional).

## 10. Cross-platform entity linking

`Organization.sameAs` should explicitly list every owned platform:
- Wikipedia URL
- Wikidata URL
- LinkedIn company page
- GitHub org
- X / Twitter
- YouTube channel
- Crunchbase

This is the "glue" that connects the entity across the AI knowledge graph.

## Effort vs. Impact Quadrant

| Effort | Low impact | High impact |
|--------|------------|-------------|
| **Low** | LinkedIn presence | Add `sameAs` to schema; claim G2/Capterra |
| **High** | Mass press releases | Wikipedia article; original research; founder Reddit presence |

Start with low-effort high-impact (sameAs, G2 claim, Wikidata).
