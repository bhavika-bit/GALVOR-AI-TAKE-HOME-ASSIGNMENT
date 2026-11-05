import json


def generate_concept(creator, campaign, llm):
    fields = ["handle", "persona", "persona_description", "voice", "language_use", "catchphrases", "themes", "format_habits", "what_feels_native", "what_would_feel_foreign"]
    profile = {k: creator.get(k) for k in fields if creator.get(k) is not None}
    payload = {"creator_profile_evidence": profile, "campaign": campaign,
               "approved_claims": campaign.get("approved_claims", [])}
    system = ("Create a creator-specific content brief using only the supplied profile evidence. Do not invent personal experiences, "
              "testimonials, children, routines, audience demographics or nutrition/medical claims. Use only approved_claims; "
              "if empty, make no efficacy or health claim. Include concept, hook, format, beats, CTA, claims_to_verify and evidence_used. "
              "Return valid JSON only.")
    answer = llm.complete(system, json.dumps(payload, ensure_ascii=False)) if llm else None
    if answer:
        try:
            return json.loads(answer)
        except (json.JSONDecodeError, TypeError):
            pass
    return {
        "concept": "A creator-native everyday story with a clearly disclosed, factual product introduction.",
        "hook": "Open with a topic or format explicitly supported by the creator profile.",
        "format": "Use the creator's documented recurring format; confirm execution with the creator.",
        "beats": ["Start with a familiar theme from the creator's feed", "Introduce Little Joys transparently", "Show the product accurately without unsupported claims", "Close with a simple invitation to learn more"],
        "CTA": "Discover more about Little Joys.",
        "claims_to_verify": ["No product efficacy claims supplied; obtain approved brand wording before use."],
        "evidence_used": [k for k in ["themes", "format_habits", "what_feels_native"] if profile.get(k)],
    }
