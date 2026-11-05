# Technical Approach and Product Decisions

## Architecture and decision design

Creator selection asks three distinct questions: **does the creator's organic content perform, does their content fit this campaign, and is the partnership appropriate for the brand?** Separate evaluators make those trade-offs inspectable instead of hiding them in one opaque model. The Decision Agent combines their outputs into one deterministic ranking; it does not let three agents compete for the final choice. This keeps specialist components focused on evidence and the final decision reproducible.

## Scoring and rationale

The supplied `config.json` sets **performance 0.35, semantic 0.40, brand 0.25**. The overall score is the weighted mean divided by the sum of configured non-negative weights. Semantic fit receives the largest weight because this is an awareness/consideration brief where creator-native relevance matters; organic performance is a supporting signal and brand compatibility is a fit/safety screen. These are explicit product-judgement weights, not trained coefficients or validated predictors. The score is heuristic suitability, not probability of success.

Performance subweights are reach 40%, visible engagement 30%, share rate 15%, consistency 15%. Median plays, visible engagement and share rate become percentiles within this 20-creator pool. Consistency is `100 / (1 + CV)` (neutral 50 when fewer than three positive-play observations exist); notably, this component is **not** percentile-ranked. Zero-like posts are excluded from visible engagement because zero may mean hidden likes; zero reshares count when observed. The supplied 392 posts contain no zero or missing likes, so that safeguard is not exercised in this snapshot.

Semantic evaluation compares creator profile/post text with the campaign brief plus up to 60 ad-creative text records. Sentence Transformers (`all-MiniLM-L6-v2`) is attempted when enabled; model/import/encoding failure falls back to lexical Jaccard similarity. The reported semantic score is a within-pool percentile, not raw similarity. Brand score is a heuristic: base 45; +15 for natural-integration guidance; +15 for parent/child/family themes; up to +25 for keyword overlap; −15 for any configured risk phrase; clipped to 0–100. These design choices favour transparent rules over pretending a trained outcome model exists when no verified campaign outcome labels are supplied.

## Missing data, memory and LLM

Audience data is attached only when present; nothing is imputed. Only 3/20 creators have audience records, and none of the selected five does. Availability is evidence only—it does **not** change the numeric brand score. The profile field `what_would_feel_foreign` is also not scored. Risk phrases are a small review prompt, not a compliance classifier.

Brand memory stores creator, public-ad-creative, brand and brief evidence with SHA-256-based deduplication and simple token-overlap retrieval. The current file has 120 records. It does not fabricate outcome memory; only verified campaign results should be added later with source and measurement context.

Gemini/Groq are optional. Current provider is `none`; missing keys, request failures or invalid JSON lead to deterministic fallbacks. LLM text can draft evidence-bound explanations/concepts but never decides the ranking. Approved claims are currently empty. Human review is required for AI labels, creator/audience facts, disclosure, child safeguarding, medical/professional endorsement and all nutrition/health claims.

## What the system cannot establish

It cannot predict paid ROAS, prove incremental impact, verify audience authenticity/current demographics, confirm creator availability/fees, guarantee AI-label accuracy or determine legal compliance. Public ad creative is used as creative reference; ad spend/impression/click/purchase/revenue values are synthetic exercise data. Organic creator metrics are not paid outcomes.

## What I would build with one additional week

1. Add human verification and provenance for AI-generated creator/post labels.
2. Improve current audience-data coverage and source/definition consistency.
3. Explain semantic matches with post-level snippets, links and visible model/fallback status.
4. Add tests for missing/malformed data, duplicate handles, hidden metrics, unavailable model/API, memory deduplication and shortlist uniqueness; harden confidence/error handling.
5. Define campaign measurement and a feedback loop that adds only verified reach, spend, view, click and conversion outcomes with attribution windows and sources.
6. Validate weights retrospectively and prospectively against real outcomes before claiming predictive performance.
