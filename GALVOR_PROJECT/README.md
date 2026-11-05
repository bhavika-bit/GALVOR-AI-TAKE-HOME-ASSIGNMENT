# Little Joys Creator Intelligence Engine

A Streamlit prototype for Galvor's tech intern assignment. It evaluates 20 Instagram creators using specialist evidence layers, ranks five recommendations, and creates cautious creator-specific content briefs.

## Run locally

1. Use Python 3.10+.
2. Open a terminal in this project folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. The four supplied assignment CSVs are already in `data/`. If you move them, update `data_paths` in `config.json`.
5. Optional: copy `.env.example` to `.env`, choose `gemini` or `groq` in `config.json`, and add the corresponding API key. The app works without an API key using deterministic explanations and content-brief fallbacks.
6. Launch:
   ```bash
   streamlit run app.py
   ```

## Components

- `data_loader.py`: loads configured CSVs, validates expected schema and reports data health.
- `performance_evaluator.py`: compares organic creator post metrics using cross-creator percentiles. Hidden/zero-like posts are handled cautiously.
- `semantic_evaluator.py`: compares creator profiles/posts with the campaign brief and ad creative context using sentence embeddings, with a lexical fallback.
- `brand_evaluator.py`: checks natural-integration guidance, family/parenting relevance, available audience data and review flags.
- `brand_memory.py`: persistent, deduplicated brand/creator/creative evidence store. It does not invent campaign outcomes.
- `decision_agent.py`: transparent weighted scoring plus five distinct recommendation roles.
- `creative_generator.py`: generates evidence-grounded creator briefs; no unapproved nutrition or medical claims.
- `llm_client.py`: optional Gemini/Groq API wrapper. API keys are read from `.env` and must never be committed.

## Scoring and interpretation

The default weights in `config.json` are performance 35%, semantic fit 40%, and brand compatibility 25%. These are **heuristic judgement weights**, not coefficients learned from historical creator campaign outcomes. The performance evaluator uses relative percentiles across this 20-creator sample for median plays, visible engagement, share rate and consistency. A score is a comparative suitability indicator, not a probability of success.

The five recommendation roles are: (1) primary weighted recommendation, (2) highest performance-led alternative, (3) highest semantic-fit alternative, and (4–5) next-best overall creators, with duplicates skipped.

## Critical data caveats

- `ads.csv` contains real public ad creative and metadata, but its spend, impressions, views, clicks, carts, purchases and revenue values are synthetic exercise data. Any ROAS/CTR derived from them is descriptive exercise analysis only.
- `creator_posts.csv` contains organic public post metrics. Organic plays/engagement must not be represented as paid campaign outcomes or a paid ROAS forecast.
- Audience demographics exist for only 3 of 20 creators. The other 17 are marked unavailable, never imputed from content or creator identity.
- AI-added labels such as hook type, format, child presence and topic can be wrong. Treat them as signals and manually inspect source posts/ads before relying on them.
- Some creators hide likes; zero/low values are not automatically interpreted as true zero engagement.
- Product efficacy, health and nutrition claims must be checked against approved brand wording. Empty `approved_claims` means the generated concepts avoid efficacy claims.
- Any keyword risk flag is a human-review prompt, not a legal/compliance conclusion.

## Outputs

After a run, the app writes `outputs/creator_evaluations.csv`, `outputs/top_five.csv`, `outputs/top_five.json`, and a deduplicated `outputs/brand_memory.json`.

## AI use and human review

The embedding model supports semantic matching. If enabled, its first run may download model weights. Gemini/Groq are optional for structured explanations and creative concepts. All outputs should be checked by a human for factual accuracy, creator fit, advertising disclosure, child safety, and claim compliance before submission or campaign use.
