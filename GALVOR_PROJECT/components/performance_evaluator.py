import numpy as np
import pandas as pd
from .utils import handle, col, score


def _percentile(values):
    """Comparable cross-creator percentile; missing values remain neutral (50)."""
    s = pd.to_numeric(values, errors="coerce")
    result = s.rank(pct=True, method="average") * 100
    return result.fillna(50.0)


def evaluate_performance(creators, posts):
    if "handle" not in creators:
        raise ValueError("creators.csv must contain handle")
    p = posts.copy()
    for c in ["plays", "likes", "comments", "reshares"]:
        if c in p:
            p[c] = pd.to_numeric(p[c], errors="coerce")
    post_handle = col(p, ["handle"])
    if post_handle is None:
        raise ValueError("creator_posts.csv must contain handle")

    raw = []
    for _, creator in creators.iterrows():
        h = handle(creator["handle"])
        cp = p[p[post_handle].map(handle) == h].copy()
        plays = cp["plays"].where(cp["plays"] > 0).dropna() if "plays" in cp else pd.Series(dtype=float)
        median_plays = float(plays.median()) if len(plays) else np.nan

        # A zero like count can mean hidden likes; exclude zero-like rows from visible engagement rates.
        engagement = np.nan
        if {"plays", "likes"}.issubset(cp.columns):
            valid = cp[(cp["plays"] > 0) & (cp["likes"] > 0)]
            interactions = valid["likes"].fillna(0)
            for metric in ["comments", "reshares"]:
                if metric in valid:
                    interactions = interactions + valid[metric].fillna(0)
            if len(valid):
                engagement = float((interactions / valid["plays"] * 100).median())
        share_rate = np.nan
        if {"plays", "reshares"}.issubset(cp.columns):
            valid_share = cp[(cp["plays"] > 0) & cp["reshares"].notna()]
            if len(valid_share):
                share_rate = float((valid_share["reshares"] / valid_share["plays"] * 100).median())

        cv = np.nan
        if len(plays) >= 3 and plays.mean() > 0:
            cv = float(plays.std(ddof=0) / plays.mean())
        consistency = 100 / (1 + cv) if np.isfinite(cv) else np.nan
        raw.append({
            "handle": creator["handle"], "post_count_used": int(len(cp)),
            "posts_with_play_data": int(len(plays)), "median_plays": median_plays,
            "median_visible_engagement_pct": engagement, "median_share_rate_pct": share_rate,
            "consistency_raw": consistency,
        })

    result = pd.DataFrame(raw)
    result["reach_score"] = _percentile(result["median_plays"])
    result["engagement_score"] = _percentile(result["median_visible_engagement_pct"])
    result["share_score"] = _percentile(result["median_share_rate_pct"])
    result["consistency_score"] = pd.to_numeric(result["consistency_raw"], errors="coerce").fillna(50)
    # Heuristic weights, disclosed in the README/config; not a trained prediction model.
    result["performance_score"] = (
        .40 * result["reach_score"] + .30 * result["engagement_score"] +
        .15 * result["share_score"] + .15 * result["consistency_score"]
    ).map(score).round(1)
    result["performance_evidence"] = result.apply(
        lambda r: (f"{int(r.post_count_used)} posts; median plays " +
        (f"{r.median_plays:,.0f}" if pd.notna(r.median_plays) else "unavailable") +
        "; median visible engagement " +
        (f"{r.median_visible_engagement_pct:.2f}%" if pd.notna(r.median_visible_engagement_pct) else "unavailable/hidden") +
        "; organic post metrics only"), axis=1)
    return result.drop(columns=["consistency_raw"])
