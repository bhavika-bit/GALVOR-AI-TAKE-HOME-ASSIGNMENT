import re
import pandas as pd
from .utils import txt, handle, score

RISK_TERMS = ["cure", "treats", "prevents disease", "guaranteed", "clinically proven", "doctor approved"]


def evaluate_brand(creators, audience, campaign):
    if "handle" not in creators:
        raise ValueError("creators.csv must contain handle")
    audience_by_handle = {}
    if not audience.empty and "handle" in audience:
        audience_by_handle = {handle(r["handle"]): r for _, r in audience.iterrows()}
    rows = []
    target = txt(campaign.get("target_audience", "")).lower()
    campaign_terms = set(re.findall(r"[a-z0-9]+", " ".join([target, txt(campaign.get("product", "")), " ".join(campaign.get("keywords", []))]).lower()))
    stop = {"the", "and", "for", "with", "of", "in", "to", "a", "an", "on", "india", "indian", "brand", "campaign", "young"}
    campaign_terms -= stop
    for _, creator in creators.iterrows():
        h = handle(creator["handle"])
        aud = audience_by_handle.get(h)
        native = txt(creator.get("what_feels_native", ""))
        foreign = txt(creator.get("what_would_feel_foreign", ""))
        themes = " ".join(txt(creator.get(c, "")) for c in ["persona", "persona_description", "feed_story", "themes", "audience_read"]).lower()
        risk_text = " ".join(txt(creator.get(c, "")) for c in ["bio", "persona", "feed_story", "voice", "themes", "what_feels_native", "what_would_feel_foreign"]).lower()
        flags = [term for term in RISK_TERMS if term in risk_text]
        parent_terms = ["parent", "mother", "mom", "motherhood", "child", "baby", "family", "kids", "infant"]
        thematic_fit = any(term in themes for term in parent_terms)
        # Audience match is only scored when actual audience data exists. No demographic inference for other creators.
        age_text = txt(aud.get("age_split", "")) if aud is not None else ""
        country_text = txt(aud.get("top_countries", "")) if aud is not None else ""
        city_text = txt(aud.get("top_cities", "")) if aud is not None else ""
        audience_evidence = "Audience demographics unavailable; not imputed." if aud is None else (
            f"Audience data available ({txt(aud.get('platform',''))}, as of {txt(aud.get('as_of',''))}); "
            f"women {txt(aud.get('women_pct','NA'))}%, men {txt(aud.get('men_pct','NA'))}%; "
            f"age: {age_text}; countries: {country_text}; cities: {city_text}."
        )
        profile_text = " ".join([themes, native.lower()])
        profile_terms = set(re.findall(r"[a-z0-9]+", profile_text)) - stop
        keyword_overlap = len(campaign_terms & profile_terms) / max(1, len(campaign_terms))
        brand_score = 45 + (15 if native else 0) + (15 if thematic_fit else 0) + (25 * keyword_overlap) - (15 if flags else 0)
        rows.append({
            "handle": creator["handle"], "brand_score": round(score(brand_score), 1),
            "audience_data_available": aud is not None,
            "audience_platform": txt(aud.get("platform", "")) if aud is not None else "Unavailable",
            "audience_age_split": age_text, "audience_top_cities": city_text,
            "audience_top_countries": country_text,
            "previous_brand_partnerships": txt(aud.get("brands_in_past_year", "")) if aud is not None else "Unavailable",
            "risk_flags": "; ".join(flags) if flags else "No configured keyword flag detected; human review still required",
            "brand_evidence": ("Natural integration guidance present. " if native else "No explicit natural-integration guidance. ") +
                ("Parent/child/family themes appear in profile/feed read. " if thematic_fit else "Parent/child/family relevance not clearly evidenced in profile/feed read. ") + audience_evidence,
        })
    return pd.DataFrame(rows)
