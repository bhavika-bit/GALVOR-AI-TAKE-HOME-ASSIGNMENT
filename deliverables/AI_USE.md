# AI Use Documentation

## Scope of AI assistance

AI assistance was used during development and preparation of this assignment for:

- Architecture exploration and implementation support for a Streamlit creator-intelligence prototype.
- Code generation and refinement across data loading, evaluator components, decision synthesis, memory, optional LLM integration and the UI.
- Semantic-analysis design, including embedding-based matching and a lexical fallback.
- Drafting evidence-bound creator concepts and campaign communication briefs.
- Documentation, debugging support and review of implementation/data caveats.

This document describes the development workflow at a high level. It is **not an exported session transcript** and does not claim to reproduce exact historical prompts. No original prompt/session log was present in the supplied repository.

## Human guardrails and accountability

- **Auditable ranking:** the final shortlist is produced by deterministic Python scoring and configured weights. LLM text generation does not determine the final rank.
- **Evidence-bound generation:** creator-specific concepts and explanations are constrained to supplied creator/profile/campaign evidence. Generated copy remains a draft requiring human verification.
- **No invented audience data:** missing demographics are marked unavailable; content style or creator identity is not used to infer them.
- **No fabricated outcomes:** organic creator metrics remain separate from synthetic ad-account exercise values. Brand memory does not invent campaign outcome records.
- **Claims control:** the current `approved_claims` list is empty. Product efficacy, health, growth, immunity, treatment or medical claims must not be introduced without brand-approved wording and substantiation.
- **Safety and compliance:** a human must review creator identity, source posts, AI-added labels, audience quality, advertising disclosure, child safeguarding/consent, professional endorsements, usage rights and regulatory requirements before campaign execution.
- **Fallback behaviour:** optional Gemini/Groq calls may fail or be disabled. The application is designed to continue with deterministic explanations and concept templates rather than inventing a successful API result.

## Known limitations

AI-generated profile and post labels can be inaccurate; keyword risk checks are not compliance decisions; semantic scores are relative to this dataset and query; and the system does not predict paid ROAS or establish campaign causality. A human owner remains responsible for approval and final decisions.
