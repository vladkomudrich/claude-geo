# GEO Research Base (May 2026)

Condensed evidence base for every claim this skill makes. Each statistic is
tagged with its source quality: **[verified]** = primary source confirmed,
**[secondary]** = industry tracking / commentary, **[estimate]** = widely
circulated but not directly verified in primary source.

## Scale of AI-driven search (May 2026)

- AI Overviews appear in **48% of Google queries** (+58% since Dec 2025), 200 countries, 40 languages. **[verified]** Google blog.
- Google AI Mode: **75M daily active users** (4× growth since May 2025), 1B+ queries/month US+India. 53 additional languages launched Mar 2026. **[verified]** Google blog.
- ChatGPT scale: ~800M weekly active users, ~50M shopping queries/day. **[estimate]** Not directly confirmed by OpenAI public sources.
- AI-referred traffic grew **+527% YoY** (H1 2025). **[secondary]** SparkToro.
- LLM-referred traffic converts **4-23× higher** than organic search:
  - B2B/eCom average: 14.2% conversion vs 2.8% organic.
  - B2B SaaS: 23× (Ahrefs internal data).
  - News/publishers: 17× (Microsoft Clarity Copilot study, 1,277 domains).
  - Shopify e-comm: +50% conversion rate, +14% AOV.
- **93% of AI Mode queries** are zero-click. **[secondary]** Seer Interactive 25.1M impressions.
- AI Overview citations correlate with **+120% organic clicks per impression**, +35% organic CTR, +91% paid CTR. **[secondary]** Seer Interactive.
- Gartner projects **25% of searches** shift to generative engines by 2028. **[secondary]** Gartner.

## Validated tactic effect sizes

| Tactic | Effect | Source |
|--------|--------|--------|
| Statistics Addition | **+41%** visibility (PAWC) | KDD '24 GEO paper |
| Quotation Addition | **+28%** Subjective Impression | KDD '24 |
| Cite Sources | major boost for factual queries | KDD '24 |
| Fluency + Easy-to-Understand | +15-30% visibility | KDD '24 |
| Comparison pages with 3+ tables | **+25.7%** citations | AirOps 2026 |
| 8+ list sections on a page | **+26.9%** citations | AirOps 2026 |
| Avg sentence length ≤ 10 words | **+18.8%** citations | AirOps 2026 |
| Tables vs prose | 81% vs 23% extraction rate | 2026 citation studies |
| 3+ schema types on a page | +13% citation likelihood | AirOps 2026 |
| Page updated within 12 months | 3× less likely to lose visibility | AirOps 2026 |
| Keyword stuffing | ~0% effect | KDD '24 + Google official |

## Content structure findings

- **44.2%** of LLM citations come from the **first third** of a page, 31.1% middle, 24.7% end. Front-loading is mandatory.
- Tables extracted **81%** of the time vs **23%** for equivalent prose.
- Pages >20,000 chars average **10.18 citations**; pages <500 chars average 2.39.
- Self-contained 50-150-word passages get **2.3× more citations** than long unstructured prose.
- Optimal RAG chunk size: **256-512 tokens** with recursive splitting (best performer Feb 2026: 69% accuracy on 50 academic papers).
- Bullet content with 5-7 items is cited more frequently than equivalent prose.

## Schema findings

- **FAQPage rich results deprecated 7 May 2026** by Google. The schema itself remains valid; ChatGPT/Perplexity/Gemini extract from it. FAQPage pages are **3.2× more likely** to appear in Google AI Overviews.
- **HowTo rich results** retired Sept 2023.
- **knowsAbout** property on Organization/Person became the #2 most important markup element after Mar 2026 (Gemini 3 AI Mode uses it for source selection).
- **sameAs** identifiers connecting Org/Person to Wikipedia/LinkedIn/GitHub improve entity recognition.
- Entity-chain depth (Product → Manufacturer → Organization → Founder → Person) outperforms 10 disconnected @types.
- **Ahrefs schema study (1,885 pages):** adding schema alone gave no major citation uplift; effect inseparable from concurrent SEO/content/links investment.
- **BrightEdge:** sites with structured data + FAQ blocks saw +44% AI search citations.
- **AirOps:** 61% of cited pages use 3+ schema types.

## Off-site presence findings

- Brands with Wikipedia get first ChatGPT citation in **28 days avg** vs **52 days** without.
- G2/Capterra/Trustpilot **aggregate rating <4.0** acts as a **filter** blocking ChatGPT citation in competitive queries.
- Reddit organic participation: **3.4× citation lift**.
- Brands with millions of Reddit/Quora mentions are ~4× more likely cited overall.
- ~48% of AI citations come from community platforms (Reddit, YouTube).
- **Brand mentions ≠ citations.** AirOps: brands with both mention and citation are 40% more likely to reappear in subsequent answers. Zapier #1 cited in tech, only #44 in mention rank — two distinct strategies.

## llms.txt reality check (May 2026)

- Adoption: **10.13%** of 300K domains surveyed (SE Ranking).
- Google publicly stated its AI systems **do not use** llms.txt.
- ChatGPT, Claude, Perplexity: no public confirmation of llms.txt retrieval.
- **BUT:** IDE agents (Cursor, Continue, Cline, Aider) and MCP documentation servers actively consume llms.txt.
- **Recommendation:** Worth implementing for developer-tool products. Lower priority for non-developer-facing products.

## CITABLE framework (Discovered Labs)

Reports **+340% AI citations in 90 days** when fully applied:

- C — Clear entity structure (BLUF).
- I — Intent architecture (Q-style H2s + direct answers).
- T — Third-party validation.
- A — Answer grounding (specific numbers).
- B — Block structure for RAG (50-150 word capsules).
- L — Latest timestamps (visible + dateModified).
- E — Entity schema (Org + knowsAbout + sameAs).

Additional 2026 cases:
- B2B SaaS project mgmt: 288% ROI / 3.9× return in 90 days (€16,485 → €64,000 closed revenue).
- 300-500% AI-citation increases, 250-400% qualified-lead growth, 40-60% sales cycle reduction across multiple B2B cases.
- CRM manufacturing: +450% AI citations in 6 months, appearance in 65% of relevant AI responses.

## Reddit citation share trajectory (Oct 2025 - Jan 2026)

| Event | Effect |
|-------|--------|
| Reddit-Perplexity lawsuit (Oct 2025) | -86% Perplexity Reddit citations almost immediately |
| ChatGPT parameter shift (Q4 2025) | Reddit share fell 60% → 10% in 6 weeks |
| YouTube absorption (Q4 2025 - Q1 2026) | Replaced Reddit slot in Perplexity |
| PR Newswire / Forbes / Medium rise | Filled Reddit slot in ChatGPT |
| Overall Reddit citations | +73% Oct 2025 → Jan 2026 across all engines combined |
| Perplexity Reddit recovery | Climbed back to 24% citation share by Jan 2026 |

## Three-bot framework (Anthropic)

| Bot | Purpose | Supports Crawl-delay |
|-----|---------|---------------------|
| ClaudeBot | Training | Yes |
| Claude-User | User-initiated fetches | n/a |
| Claude-SearchBot | Search index | n/a |

**Retired (do not add):** `anthropic-ai`, `claude-web` (retired July 2024).

## Agentic Commerce Protocol (ACP)

- **Launched 29 Sept 2025**, Apache 2.0, maintained by OpenAI + Stripe.
- Status: **beta**.
- Etsy US sellers: LIVE at launch. Shopify (1M+ merchants): "coming soon".
- Mechanism: Delegate Payment (spec) / Shared Payment Token (Stripe impl).
- Merchant remains merchant of record.

## Tools landscape

**Free / freemium:**
- Ahrefs Brand Radar (243M+ prompt base)
- HubSpot AEO Grader
- AnswerSocrates LLM Brand Tracker

**Mid-tier ($50-500/mo):**
- HubSpot AEO ($50/mo)
- AthenaHQ (SOC 2 Type II, GDPR; 85M sources, 90+ countries, GA4 native)
- Peec AI (UI-scraping not API-sampling, GA4 native)
- SE Ranking, Otterly.AI, AIclicks

**Enterprise:**
- Profound (G2 Winter 2026 Leader, Sequoia-backed, from $399/mo)
- Scrunch AI ($15M+ funding; Lenovo, Clerk, Skims, Penn State customers)
- Adobe LLM Optimizer
- Semrush AI Visibility Toolkit
- Bluefish, GeoVector, Sight AI, LLMClicks

## Key sources to cite in reports

- KDD '24 GEO paper (Pradeep et al.): https://arxiv.org/abs/2311.09735
- MAGEO (Apr 2026): https://arxiv.org/abs/2604.19516
- SAGEO Arena (Feb 2026): https://arxiv.org/abs/2602.12187
- Citation Selection vs Absorption (Apr 2026): https://arxiv.org/html/2604.25707v1
- AirOps 2026 State of AI Search: https://www.airops.com/report/the-2026-state-of-ai-search
- Ahrefs Schema Study: https://ahrefs.com/blog/schema-ai-citations/
- SE Ranking llms.txt Study: https://seranking.com/blog/llms-txt/
- Anthropic Crawler Documentation: https://privacy.anthropic.com/en/articles/8896518
- Google AI Optimization Guide: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Stripe ACP Blog: https://stripe.com/blog/developing-an-open-standard-for-agentic-commerce
- Cloudflare Pay-Per-Crawl: https://blog.cloudflare.com/introducing-pay-per-crawl/
