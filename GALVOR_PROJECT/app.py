import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from components.data_loader import load_config, load_datasets, data_health, validate_datasets
from components.performance_evaluator import evaluate_performance
from components.semantic_evaluator import evaluate_semantic
from components.brand_evaluator import evaluate_brand
from components.brand_memory import BrandMemory
from components.decision_agent import build_decisions, get_agent_explanations
from components.creative_generator import generate_concept
from components.llm_client import LLMClient

st.set_page_config(
    page_title="Little Joys | Creator Intelligence",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent
config = load_config(ROOT / "config.json")
defaults = config.get("campaign_defaults", {})

# ---------- Design system ----------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--bg:#080d18;--panel:#101a2b;--panel2:#142137;--line:rgba(167,190,226,.13);--muted:#91a2bc;--text:#eef4ff;--cyan:#65d9e8;--violet:#9b8cff;--lime:#b6e66b;--pink:#f09acb}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:radial-gradient(ellipse at 80% -10%,rgba(84,104,190,.18),transparent 38%),radial-gradient(ellipse at 5% 20%,rgba(44,174,190,.10),transparent 32%),var(--bg);color:var(--text)}
[data-testid="stHeader"]{background:rgba(8,13,24,.72)}
.block-container{max-width:1540px;padding-top:1.65rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#101a2b,#0b1321);border-right:1px solid var(--line)}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] label{color:#c8d4e7}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{font-family:Manrope;color:#f3f7ff}
.stButton>button{border-radius:11px;border:1px solid rgba(120,220,235,.35);background:linear-gradient(110deg,#276a83,#5a55a7);color:white;font-weight:700;min-height:2.8rem;box-shadow:0 8px 26px rgba(57,123,170,.18)}
.stButton>button:hover{border-color:#8ce8f2;color:white;filter:brightness(1.12)}
[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(21,36,59,.95),rgba(13,24,41,.95));border:1px solid var(--line);padding:16px 18px;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.12)}
[data-testid="stMetricLabel"]{color:#9fb0c9!important;font-size:.78rem}
[data-testid="stMetricValue"]{color:#f2f7ff!important;font-family:Manrope;font-weight:800}
.stTabs [data-baseweb="tab-list"]{gap:8px;border-bottom:1px solid var(--line)}
.stTabs [data-baseweb="tab"]{background:rgba(18,30,49,.7);border:1px solid var(--line);border-radius:10px 10px 0 0;color:#aab9ce;padding:10px 17px}
.stTabs [aria-selected="true"]{background:rgba(77,117,163,.22)!important;color:#eaf7ff!important;border-color:rgba(101,217,232,.35)!important}
[data-testid="stDataFrame"],.stAlert{border-radius:14px}
hr{border-color:var(--line)}
.eyebrow{font-size:.68rem;letter-spacing:.19em;text-transform:uppercase;color:var(--cyan);font-weight:700}
.page-title{font:800 2rem Manrope,sans-serif;color:#f3f7ff;letter-spacing:-.04em;margin:.2rem 0 .25rem}
.subtle{color:var(--muted);font-size:.91rem}
.hero{position:relative;overflow:hidden;padding:28px 30px;border-radius:22px;border:1px solid rgba(129,174,226,.23);background:linear-gradient(112deg,rgba(22,48,77,.98),rgba(37,43,83,.96) 58%,rgba(42,40,81,.96));box-shadow:0 22px 65px rgba(0,0,0,.24);margin:8px 0 20px}
.hero:after{content:'';position:absolute;width:340px;height:340px;right:-80px;top:-170px;border-radius:50%;background:radial-gradient(circle,rgba(102,220,235,.24),transparent 68%)}
.hero h1{font:800 2.15rem Manrope,sans-serif;letter-spacing:-.045em;color:#f6f9ff;margin:.35rem 0 .45rem;max-width:780px}
.hero p{color:#c2d0e6;margin:0;max-width:730px;font-size:.96rem}
.hero-chip{display:inline-block;border:1px solid rgba(143,221,232,.3);background:rgba(89,177,195,.12);color:#b9f3f5;padding:5px 10px;border-radius:30px;font-size:.72rem;font-weight:700;margin-right:6px}
.section-head{font:750 1.18rem Manrope;color:#f0f5ff;margin:1.1rem 0 .2rem}
.section-note{color:var(--muted);font-size:.82rem;margin-bottom:13px}
.primary-card{position:relative;overflow:hidden;border-radius:22px;padding:25px 27px;border:1px solid rgba(112,224,225,.35);background:radial-gradient(ellipse at 100% 0%,rgba(90,104,190,.23),transparent 40%),linear-gradient(135deg,#152c43,#18243e 58%,#252448);box-shadow:0 18px 55px rgba(0,0,0,.28);margin:12px 0 18px}
.primary-card:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:linear-gradient(180deg,var(--cyan),var(--violet))}
.primary-top{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:15px}
.primary-badge{font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#08131d;background:linear-gradient(90deg,#8de9e8,#b8e879);padding:6px 10px;border-radius:7px}
.rank-pill{font-size:.72rem;color:#c4d3e8;border:1px solid var(--line);padding:5px 9px;border-radius:20px}
.creator-name{font:800 1.7rem Manrope;color:#f6f9ff;letter-spacing:-.035em;margin:0}
.creator-handle{color:#9fb4ce;font-size:.9rem;margin:.1rem 0 .65rem}
.creator-desc{color:#c4d2e7;font-size:.9rem;line-height:1.55;max-width:800px}
.score-orb{border:1px solid rgba(121,224,230,.34);background:rgba(7,17,30,.34);border-radius:18px;padding:16px 18px;text-align:center;min-width:120px}
.score-orb strong{font:800 2rem Manrope;color:#a9f0eb;display:block;line-height:1.1}
.score-orb span{font-size:.68rem;color:#aebfd5;text-transform:uppercase;letter-spacing:.12em}
.score-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:19px}
.score-tile{background:rgba(4,13,25,.28);border:1px solid rgba(166,193,224,.12);border-radius:12px;padding:11px 13px}
.score-tile .label{font-size:.72rem;color:#9eafc7;margin-bottom:5px}
.score-tile .number{font:700 1.12rem Manrope;color:#eef8ff}
.score-track{height:5px;border-radius:20px;background:rgba(180,200,230,.13);overflow:hidden;margin-top:8px}
.score-fill{height:100%;border-radius:20px;background:linear-gradient(90deg,#63d9e5,#9b8cff)}
.evidence-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:14px}
.evidence{border:1px solid rgba(174,197,226,.13);background:rgba(8,17,30,.24);padding:12px;border-radius:12px;color:#b7c6da;font-size:.78rem;line-height:1.45}
.evidence b{display:block;color:#e6f0ff;font-size:.74rem;margin-bottom:4px}
.rec-row{display:flex;align-items:center;gap:13px;border:1px solid var(--line);background:linear-gradient(110deg,rgba(17,29,48,.92),rgba(14,24,40,.92));padding:13px 15px;border-radius:14px;margin:8px 0}
.rec-rank{width:34px;height:34px;display:grid;place-items:center;border-radius:10px;background:rgba(116,139,188,.16);color:#dbe7ff;font:800 .9rem Manrope;flex-shrink:0}
.rec-title{font-weight:700;color:#edf4ff;font-size:.9rem}
.rec-sub{color:#91a4bf;font-size:.75rem;margin-top:2px}
.rec-score{margin-left:auto;text-align:right;white-space:nowrap;color:#b5f0e8;font:800 1rem Manrope}
.role-tag{font-size:.64rem;color:#b9c9e0;border:1px solid var(--line);border-radius:20px;padding:4px 7px;display:inline-block;margin-top:5px}
.agent-card{height:100%;padding:16px;border:1px solid var(--line);background:linear-gradient(145deg,rgba(21,35,57,.9),rgba(13,23,39,.92));border-radius:16px}
.agent-icon{width:35px;height:35px;display:grid;place-items:center;border-radius:11px;background:rgba(115,142,204,.17);font-size:1rem;margin-bottom:10px}
.agent-title{font:700 .95rem Manrope;color:#edf4ff}
.agent-caption{font-size:.76rem;color:#91a5c0;line-height:1.45;margin-top:5px}
.small-kicker{font-size:.67rem;letter-spacing:.12em;text-transform:uppercase;color:#8fa4c1;font-weight:700}
div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:13px;background:rgba(14,24,40,.52)}
@media(max-width:850px){.score-grid,.evidence-grid{grid-template-columns:1fr}.hero h1{font-size:1.65rem}.primary-card{padding:19px}}
</style>
""", unsafe_allow_html=True)


def esc(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return html.escape(str(value))


def number(value, default=0):
    try:
        n = float(value)
        return default if pd.isna(n) else n
    except (TypeError, ValueError):
        return default


def score_tile(label, value):
    value = max(0, min(100, number(value)))
    return f'''<div class="score-tile"><div class="label">{esc(label)}</div><div class="number">{value:.1f}<span style="font-size:.7rem;color:#91a5c0"> / 100</span></div><div class="score-track"><div class="score-fill" style="width:{value}%"></div></div></div>'''


def evidence_box(title, value):
    value = str(value or "Evidence not available in supplied data.")
    return f'<div class="evidence"><b>{esc(title)}</b>{esc(value[:300])}</div>'


# ---------- Campaign controls ----------
with st.sidebar:
    st.markdown('<div class="eyebrow">LITTLE JOYS / GALVOR</div>', unsafe_allow_html=True)
    st.markdown("## Campaign workspace")
    st.caption("Set the brief, then run the evaluator network.")
    campaign = {
        "product": st.text_input("Product", defaults.get("product", "Little Joys product")),
        "objective": st.text_input("Objective", defaults.get("objective", "Awareness and consideration")),
        "target_audience": st.text_input("Target audience", defaults.get("target_audience", "Parents of young children")),
        "preferred_language": st.text_input("Preferred language", defaults.get("preferred_language", "Hinglish")),
        "creative_direction": st.text_area("Creative direction", defaults.get("creative_direction", "Authentic everyday storytelling"), height=90),
        "keywords": defaults.get("keywords", []),
        "approved_claims": [x.strip() for x in st.text_area("Approved claims (one per line)", "\n".join(defaults.get("approved_claims", [])), height=80).splitlines() if x.strip()],
    }
    st.markdown("---")
    st.markdown('<div class="small-kicker">Workspace settings</div>', unsafe_allow_html=True)
    st.caption("CSV paths and evaluator weights: config.json")
    st.caption("Optional LLM credentials: .env")
    st.caption("No API key? The analysis still runs with deterministic fallbacks.")

st.markdown('''<div class="hero"><div class="hero-chip">✳ CREATOR INTELLIGENCE</div><div class="hero-chip">MULTI-AGENT EVALUATION</div><h1>Find the creators who can make Little Joys feel like part of real life.</h1><p>One evidence-led decision layer, three specialist evaluators, and five actionable creator recommendations — with the primary choice clearly in focus.</p></div>''', unsafe_allow_html=True)

llm_cfg = config.get("llm", {})
llm = LLMClient(llm_cfg.get("provider", "none"), llm_cfg.get("model"))
frames, missing = load_datasets(config)
if missing:
    st.error("One or more data files could not be found. Check data_paths in config.json.")
    st.code("\n".join(missing))
    st.stop()
issues = validate_datasets(frames)
if issues:
    with st.expander("Dataset checks need attention", expanded=True):
        for issue in issues:
            st.warning(issue)

with st.expander("Dataset health & schema", expanded=False):
    st.json(data_health(frames))
    for name, df in frames.items():
        st.caption(f"{name}.csv · {len(df):,} rows · columns")
        st.code(", ".join(map(str, df.columns)))

st.markdown('<div class="subtle">Data note: ad-account spend and conversion values are synthetic exercise data. Creator post metrics are organic public-post metrics. The dashboard does not predict paid ROAS.</div>', unsafe_allow_html=True)

run_col, hint_col = st.columns([1, 2])
with run_col:
    run_clicked = st.button("✦  Run creator intelligence", type="primary", use_container_width=True)
with hint_col:
    st.markdown('<div class="subtle" style="padding:12px 2px">The Decision Agent makes the primary selection by combining performance, semantic fit and brand compatibility. Specialist evaluators provide evidence — they do not compete as separate final decision-makers.</div>', unsafe_allow_html=True)

if run_clicked:
    try:
        with st.spinner("The evaluator network is reviewing creator performance, content fit and brand compatibility…"):
            ads, creators, posts, audience = (frames[k] for k in ["ads", "creators", "posts", "audience"])
            perf = evaluate_performance(creators, posts)
            sem = evaluate_semantic(creators, posts, ads, campaign, config)
            brand = evaluate_brand(creators, audience, campaign)
            all_rows, top = build_decisions(creators, perf, sem, brand, config, campaign)

            memory_path = ROOT / config.get("output_dir", "outputs") / "brand_memory.json"
            memory = BrandMemory(memory_path)
            memory.seed(ads, creators)
            memory.add("brand_knowledge", "Little Joys is an Indian kids nutrition brand; product categories include milk mixes and gummies.", "assignment brief")
            memory.add("campaign_brief", json.dumps(campaign, ensure_ascii=False), "current campaign brief")
            memory.save()
            retrieved = memory.retrieve(" ".join(map(str, campaign.values())), 8)
            explanations = get_agent_explanations(top, campaign, retrieved, llm)

            out = ROOT / config.get("output_dir", "outputs")
            out.mkdir(parents=True, exist_ok=True)
            all_rows.to_csv(out / "creator_evaluations.csv", index=False)
            top.to_csv(out / "top_five.csv", index=False)
            (out / "top_five.json").write_text(json.dumps({"campaign": campaign, "top_five": top.to_dict("records"), "agent": explanations}, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
            st.session_state["run"] = {"all": all_rows, "top": top, "explanations": explanations, "performance": perf, "semantic": sem, "brand": brand}
    except Exception as exc:
        st.exception(exc)

if "run" not in st.session_state:
    st.markdown('<div class="section-head">Your decision workspace is ready</div><div class="section-note">Run the evaluator network to reveal the primary creator recommendation and supporting shortlist.</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col_obj, val, label in zip(cols, [len(frames["creators"]), len(frames["posts"]), len(frames["ads"]), len(frames["audience"])], ["Creators in pool", "Organic posts", "Ad creatives", "Audience profiles"]):
        col_obj.metric(label, f"{val:,}")
    st.markdown('<div class="agent-card"><div class="small-kicker">How the decision is made</div><div class="section-head" style="margin-top:7px">Specialists analyse. The Decision Agent decides.</div><div class="subtle">Performance evaluator → Semantic evaluator → Brand compatibility evaluator → Decision Agent → Five ranked creator recommendations.</div></div>', unsafe_allow_html=True)
else:
    run = st.session_state["run"]
    all_rows, top = run["all"], run["top"]
    primary = top.iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Creators evaluated", f"{len(all_rows):,}")
    m2.metric("Organic posts analysed", f"{len(frames['posts']):,}")
    m3.metric("Ad creatives reviewed", f"{len(frames['ads']):,}")
    m4.metric("Final recommendations", f"{len(top):,}")

    st.markdown('<div class="section-head">The Decision Agent’s recommendation</div><div class="section-note">This is the primary campaign recommendation, selected from the combined evaluator evidence.</div>', unsafe_allow_html=True)
    handle_text = str(primary.get("handle", "Creator"))
    creator_title = handle_text if handle_text.startswith("@") else "@" + handle_text
    persona = primary.get("persona", primary.get("feed_story", ""))
    reason = primary.get("decision_reason", "Selected through the combined suitability score.")
    primary_html = f'''<div class="primary-card"><div class="primary-top"><span class="primary-badge">★ PRIMARY RECOMMENDATION</span><span class="rank-pill">Rank #{int(number(primary.get('rank', 1), 1))} of {len(all_rows)}</span><span class="rank-pill">{esc(primary.get('confidence', 'Not rated'))} confidence</span></div><div style="display:flex;justify-content:space-between;align-items:flex-start;gap:20px;flex-wrap:wrap"><div style="flex:1;min-width:240px"><h2 class="creator-name">{esc(creator_title)}</h2><div class="creator-handle">{esc(primary.get('persona', ''))[:120]}</div><div class="creator-desc">{esc(reason)}</div></div><div class="score-orb"><strong>{number(primary.get('overall_score')):.1f}</strong><span>Suitability score</span></div></div><div class="score-grid">{score_tile('Organic performance', primary.get('performance_score'))}{score_tile('Semantic campaign fit', primary.get('semantic_score'))}{score_tile('Brand compatibility', primary.get('brand_score'))}</div><div class="evidence-grid">{evidence_box('PERFORMANCE SIGNAL', primary.get('performance_evidence'))}{evidence_box('CONTENT / SEMANTIC FIT', primary.get('semantic_evidence'))}{evidence_box('BRAND FIT & SAFETY', primary.get('brand_evidence'))}</div></div>'''
    st.markdown(primary_html, unsafe_allow_html=True)

    tabs = st.tabs(["Decision & shortlist", "Creator intelligence", "Ad intelligence", "Method & limitations"])
    with tabs[0]:
        left, right = st.columns([1.2, .8], gap="large")
        with left:
            st.markdown('<div class="section-head">Five recommended creators</div><div class="section-note">The first choice is the Decision Agent’s primary pick. Other rows are alternatives selected for distinct strengths.</div>', unsafe_allow_html=True)
            for _, row in top.iterrows():
                h = str(row.get("handle", "Creator")); h = h if h.startswith("@") else "@" + h
                role = str(row.get("selection_role", "Alternative recommendation"))
                rank = int(number(row.get("recommendation_order", 0)))
                st.markdown(f'''<div class="rec-row"><div class="rec-rank">{rank:02d}</div><div style="min-width:0"><div class="rec-title">{esc(h)}</div><div class="rec-sub">{esc(row.get('persona',''))[:100]}</div><span class="role-tag">{esc(role)}</span></div><div class="rec-score">{number(row.get('overall_score')):.1f}<div style="font:500 .62rem 'DM Sans';color:#8fa4bf">/ 100</div></div></div>''', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="section-head">How the network contributed</div><div class="section-note">Three evidence layers feed one final decision.</div>', unsafe_allow_html=True)
            agent_cards = [
                ("◈", "Performance evaluator", "Compares organic plays, visible engagement, share signals and consistency across the creator pool.", primary.get("performance_score")),
                ("⌁", "Semantic evaluator", "Matches creator voice, themes, formats and post content with the campaign brief and ad creative patterns.", primary.get("semantic_score")),
                ("✳", "Brand compatibility", "Reviews natural integration, relevance, available audience data and risk flags for human review.", primary.get("brand_score")),
            ]
            for icon, title, desc, val in agent_cards:
                st.markdown(f'''<div class="agent-card" style="margin-bottom:9px"><div class="agent-icon">{icon}</div><div class="agent-title">{title}</div><div class="agent-caption">{desc}</div><div style="margin-top:10px;font:800 1.1rem Manrope;color:#b9eee9">{number(val):.1f}<span style="font:500 .68rem 'DM Sans';color:#91a5c0"> / 100 for primary pick</span></div></div>''', unsafe_allow_html=True)
            with st.expander("Decision Agent synthesis"):
                st.json(run["explanations"])

        st.markdown("---")
        st.markdown('<div class="section-head">Primary creator’s campaign concept</div><div class="section-note">A working creative direction generated from the creator profile. Validate claims, disclosure and execution before use.</div>', unsafe_allow_html=True)
        if st.button("Generate / refresh primary creator brief", key="primary_brief"):
            st.session_state["primary_concept"] = generate_concept(primary.to_dict(), campaign, llm)
        concept = st.session_state.get("primary_concept")
        if concept is None:
            concept = generate_concept(primary.to_dict(), campaign, llm)
            st.session_state["primary_concept"] = concept
        st.json(concept)
        if primary.get("risk_flags") and "No configured" not in str(primary.get("risk_flags")):
            st.warning("Human review flag: " + str(primary.get("risk_flags")))

    with tabs[1]:
        st.markdown('<div class="section-head">Creator pool comparison</div><div class="section-note">Use the score table to inspect the evidence layers. Scores are relative suitability indicators, not probabilities.</div>', unsafe_allow_html=True)
        display_cols = [c for c in ["rank", "handle", "followers", "post_count_used", "performance_score", "semantic_score", "brand_score", "overall_score", "confidence", "audience_data_available"] if c in all_rows]
        st.dataframe(all_rows[display_cols], use_container_width=True, hide_index=True)
        chart_cols = [c for c in ["performance_score", "semantic_score", "brand_score", "overall_score"] if c in all_rows]
        if chart_cols:
            chart_df = all_rows.set_index("handle")[chart_cols].sort_values("overall_score", ascending=True) if "overall_score" in chart_cols else all_rows.set_index("handle")[chart_cols]
            st.bar_chart(chart_df, height=440)
        selected_handle = st.selectbox("Inspect a creator", all_rows["handle"].astype(str).tolist())
        selected = all_rows[all_rows["handle"].astype(str) == selected_handle].iloc[0]
        st.markdown(f"### @{selected_handle.lstrip('@')}")
        a, b, c = st.columns(3)
        a.metric("Overall suitability", f"{number(selected.get('overall_score')):.1f}/100")
        b.metric("Organic performance", f"{number(selected.get('performance_score')):.1f}/100")
        c.metric("Semantic fit", f"{number(selected.get('semantic_score')):.1f}/100")
        st.write(selected.get("persona", selected.get("feed_story", "No creator profile summary available.")))
        with st.expander("Evidence details"):
            st.write("**Performance:**", selected.get("performance_evidence", "Not available"))
            st.write("**Semantic fit:**", selected.get("semantic_evidence", "Not available"))
            st.write("**Brand compatibility:**", selected.get("brand_evidence", "Not available"))
            st.write("**Risk flags:**", selected.get("risk_flags", "None recorded"))

    with tabs[2]:
        ads = frames["ads"].copy()
        st.warning("The ad-account performance fields are synthetic exercise data. These are descriptive exercise patterns, not verified Little Joys results or causal findings.")
        numeric = [c for c in ["spend_inr", "impressions", "video_3s_views", "thruplays", "link_clicks", "add_to_carts", "purchases", "revenue_inr"] if c in ads]
        for c in numeric:
            ads[c] = pd.to_numeric(ads[c], errors="coerce")
        if {"spend_inr", "revenue_inr"}.issubset(ads.columns):
            ads["exercise_roas"] = ads["revenue_inr"] / ads["spend_inr"].replace(0, pd.NA)
        if {"link_clicks", "impressions"}.issubset(ads.columns):
            ads["ctr_pct"] = ads["link_clicks"] / ads["impressions"].replace(0, pd.NA) * 100
        st.markdown("#### Descriptive ad metrics")
        if numeric:
            st.dataframe(ads[numeric + [c for c in ["exercise_roas", "ctr_pct"] if c in ads]].describe().T, use_container_width=True)
        pattern_cols = [c for c in ["hook_type", "ad_format", "main_benefit", "language", "cta_type"] if c in ads]
        for c in pattern_cols:
            st.markdown(f"**{c.replace('_', ' ').title()}**")
            grouped_cols = [x for x in ["spend_inr", "impressions", "purchases", "revenue_inr"] if x in ads]
            if grouped_cols:
                st.dataframe(ads.groupby(c, dropna=False)[grouped_cols].mean().sort_values(by=grouped_cols[-1], ascending=False), use_container_width=True)
            else:
                st.dataframe(ads[c].value_counts(dropna=False).to_frame("ad_count"), use_container_width=True)

    with tabs[3]:
        st.markdown("""
        **Performance evaluator** — compares creator organic-post metrics using relative percentiles. Hidden/zero-like values are treated cautiously.

        **Semantic evaluator** — compares creator bios, feed descriptions, captions and available transcripts with the campaign brief and ad creative patterns. Embeddings are used when available; a lexical fallback is used if the model cannot load.

        **Brand compatibility evaluator** — checks natural-integration guidance, visible family/parenting relevance, available audience information and configured risk-language flags. Keyword flags are prompts for human review, not a compliance verdict.

        **Decision Agent** — combines configurable heuristic scores and selects one primary recommendation plus four distinct alternatives. The specialist evaluators provide evidence; they do not make separate competing final selections.

        **Memory** — stores brand, creator and creative knowledge with deduplication. Outcome memory remains empty until real campaign outcomes are supplied.

        **Limitations** — AI-added labels can be wrong; only 3 creators have audience data; post metrics are organic; synthetic ad performance is not actual brand performance. All selections, claims, disclosures and child-safety considerations require human review.
        """)
