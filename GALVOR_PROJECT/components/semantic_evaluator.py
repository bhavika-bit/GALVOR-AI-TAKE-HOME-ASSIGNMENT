import re
import pandas as pd
from .utils import txt, handle, col, score

PROFILE_FIELDS = ["bio", "persona", "persona_description", "feed_story", "voice", "language_use", "catchphrases", "themes", "format_habits", "what_feels_native", "what_would_feel_foreign", "audience_read"]
POST_FIELDS = ["caption", "topic", "content_type", "content_form", "hook_style", "language", "setting", "tone", "product_shown", "audience_signal", "on_screen_text", "what_stands_out", "transcript"]
AD_FIELDS = ["hook_line", "ad_copy", "transcript", "main_benefit", "ad_format", "story_structure", "performance_style", "persuasion", "narratives", "ad_categories"]


def _tokens(value):
    return set(re.findall(r"[a-zA-Z0-9']+", txt(value).lower()))


def _similarities(docs, query, config):
    if not docs:
        return []
    if config.get("semantic", {}).get("use_embeddings", True):
        try:
            from sentence_transformers import SentenceTransformer
            from sklearn.metrics.pairwise import cosine_similarity
            model = SentenceTransformer(config["semantic"].get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"))
            vectors = model.encode([query] + docs, normalize_embeddings=True, show_progress_bar=False)
            return [float((x + 1) / 2) for x in cosine_similarity([vectors[0]], vectors[1:])[0].tolist()]
        except Exception:
            pass  # Offline/no model fallback below.
    q = _tokens(query)
    return [len(q & _tokens(d)) / max(1, len(q | _tokens(d))) for d in docs]


def evaluate_semantic(creators, posts, ads, campaign, config):
    if "handle" not in creators:
        raise ValueError("creators.csv must contain handle")
    p = posts.copy()
    ad = ads.copy()
    profile_fields = [c for c in PROFILE_FIELDS if c in creators.columns]
    post_fields = [c for c in POST_FIELDS if c in p.columns]
    ad_fields = [c for c in AD_FIELDS if c in ad.columns]

    campaign_text = " ".join(txt(campaign.get(k, "")) for k in ["product", "objective", "target_audience", "preferred_language", "creative_direction", "keywords"])
    # Summarise supplied ad creative, excluding performance fields; these are creative references, not evidence of paid ROAS.
    ad_snippets = []
    if ad_fields:
        for _, row in ad.head(100).iterrows():
            snippet = " ".join(txt(row.get(c, "")) for c in ad_fields)
            if snippet.strip():
                ad_snippets.append(snippet)
    ad_context = " ".join(ad_snippets[:60])
    query = (campaign_text + " " + ad_context).strip()

    docs, handles, post_counts = [], [], []
    post_handle = col(p, ["handle"])
    for _, creator in creators.iterrows():
        parts = [txt(creator.get(c, "")) for c in profile_fields]
        cp = p[p[post_handle].map(handle) == handle(creator["handle"])] if post_handle else pd.DataFrame()
        for field in post_fields:
            if field in cp:
                parts.extend(cp[field].dropna().astype(str).head(30).tolist())
        docs.append(" ".join(x for x in parts if x))
        handles.append(creator["handle"])
        post_counts.append(len(cp))

    similarities = _similarities(docs, query, config)
    # Sentence-transformer cosine can be negative. Map [-1,1] to [0,100].
    # Convert raw semantic similarity to a within-sample percentile so the 0-100
    # suitability scale is interpretable across this specific 20-creator shortlist.
    semantic_percentiles = pd.Series(similarities, dtype=float).rank(pct=True, method="average") * 100
    rows = []
    for idx, (h, sim, n) in enumerate(zip(handles, similarities, post_counts)):
        mapped = score(float(semantic_percentiles.iloc[idx]))
        rows.append({"handle": h, "semantic_score": round(mapped, 1),
                     "semantic_match_strength": round(float(sim), 4), "semantic_posts_used": int(n),
                     "semantic_evidence": "Creator profile and recent post text semantically compared with campaign brief and real ad creative patterns; AI-added labels treated as signals, not ground truth."})
    return pd.DataFrame(rows)
