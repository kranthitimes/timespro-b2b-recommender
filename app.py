import html
from pathlib import Path

import pandas as pd
import streamlit as st

from matcher import recommend_programs, MATCHER_VERSION


# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TimesPro | Enterprise Learning Solutions",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# -----------------------------------------------------------------------------
# TimesPro-inspired visual system
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --tp-red: #ed1c24;
        --tp-red-dark: #c9141b;
        --tp-charcoal: #222222;
        --tp-ink: #30323a;
        --tp-muted: #6b7280;
        --tp-soft: #f7f7f8;
        --tp-border: #e5e7eb;
        --tp-white: #ffffff;
    }

    .stApp {
        background: #ffffff;
        color: var(--tp-ink);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.1rem;
        padding-bottom: 3rem;
    }

    /* Hide default Streamlit chrome for a cleaner client-facing experience */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* Brand bar */
    .tp-brandbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.45rem 0 1.15rem 0;
        border-bottom: 1px solid var(--tp-border);
        margin-bottom: 1.25rem;
    }

    .tp-wordmark {
        font-size: 1.55rem;
        line-height: 1;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: var(--tp-charcoal);
    }

    .tp-wordmark span {color: var(--tp-red);}

    .tp-brand-label {
        color: var(--tp-muted);
        font-size: 0.86rem;
        font-weight: 600;
    }

    /* Hero */
    .tp-hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(120deg, #1d1d1f 0%, #292929 67%, #3a2021 100%);
        border-radius: 22px;
        padding: 3.1rem 3.2rem 2.8rem 3.2rem;
        margin: 0.7rem 0 1.7rem 0;
        box-shadow: 0 18px 45px rgba(0,0,0,0.10);
    }

    .tp-hero::after {
        content: "";
        position: absolute;
        width: 330px;
        height: 330px;
        border-radius: 50%;
        right: -135px;
        top: -125px;
        background: rgba(237, 28, 36, 0.20);
    }

    .tp-kicker {
        position: relative;
        z-index: 1;
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        color: #ffffff;
        margin-bottom: 1rem;
    }

    .tp-kicker-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: var(--tp-red);
    }

    .tp-hero h1 {
        position: relative;
        z-index: 1;
        max-width: 790px;
        margin: 0;
        color: #ffffff;
        font-size: clamp(2.2rem, 4.2vw, 3.55rem);
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -0.045em;
    }

    .tp-hero p {
        position: relative;
        z-index: 1;
        max-width: 760px;
        margin: 1.15rem 0 1.45rem 0;
        color: #e5e7eb;
        font-size: 1.06rem;
        line-height: 1.65;
    }

    .tp-hero-tags {
        position: relative;
        z-index: 1;
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
    }

    .tp-hero-tag {
        padding: 0.38rem 0.72rem;
        border: 1px solid rgba(255,255,255,0.20);
        background: rgba(255,255,255,0.07);
        border-radius: 999px;
        color: #ffffff;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Section heading */
    .tp-section-head {
        margin: 2rem 0 1rem 0;
    }

    .tp-section-index {
        color: var(--tp-red);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .tp-section-head h2 {
        margin: 0;
        color: var(--tp-charcoal);
        font-size: 1.72rem;
        letter-spacing: -0.025em;
    }

    .tp-section-head p {
        margin: 0.45rem 0 0 0;
        color: var(--tp-muted);
        font-size: 0.95rem;
    }

    /* Form container */
    div[data-testid="stForm"] {
        border: 1px solid var(--tp-border);
        border-top: 4px solid var(--tp-red);
        border-radius: 18px;
        background: #ffffff;
        padding: 1.35rem 1.45rem 0.75rem 1.45rem;
        box-shadow: 0 8px 26px rgba(0,0,0,0.045);
    }

    label, .stSelectbox label, .stMultiSelect label, .stTextInput label,
    .stTextArea label {
        font-weight: 650 !important;
        color: #3f4148 !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        border-color: #dedfe3 !important;
        background: #fafafa !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--tp-red) !important;
        box-shadow: 0 0 0 1px var(--tp-red) !important;
    }

    /* Multiselect pills */
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: var(--tp-red) !important;
        color: #ffffff !important;
        border-radius: 7px !important;
    }

    /* Main action button */
    .stButton > button,
    .stFormSubmitButton > button {
        border: 1px solid var(--tp-red) !important;
        border-radius: 10px !important;
        background: var(--tp-red) !important;
        color: #ffffff !important;
        font-weight: 750 !important;
        min-height: 3rem;
        transition: all 0.16s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: var(--tp-red-dark) !important;
        border-color: var(--tp-red-dark) !important;
        box-shadow: 0 7px 18px rgba(237,28,36,0.18);
        transform: translateY(-1px);
    }

    /* Result summary */
    .tp-results-banner {
        padding: 1.2rem 1.3rem;
        border-radius: 14px;
        background: #fff6f6;
        border: 1px solid #ffd7d9;
        border-left: 5px solid var(--tp-red);
        margin: 0.8rem 0 1.25rem 0;
    }

    .tp-results-banner strong {color: var(--tp-charcoal);}
    .tp-results-banner span {color: var(--tp-muted);}

    /* Programme cards */
    .tp-program-card {
        border: 1px solid var(--tp-border);
        border-radius: 16px;
        background: #ffffff;
        margin: 0 0 1rem 0;
        overflow: hidden;
        box-shadow: 0 5px 18px rgba(0,0,0,0.045);
    }

    .tp-card-accent {
        height: 4px;
        background: var(--tp-red);
    }

    .tp-card-body {
        padding: 1.35rem 1.45rem 1.25rem 1.45rem;
    }

    .tp-card-top {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
        justify-content: space-between;
    }

    .tp-card-title {
        margin: 0;
        color: var(--tp-charcoal);
        font-size: 1.28rem;
        line-height: 1.35;
        font-weight: 760;
        letter-spacing: -0.015em;
    }

    .tp-card-meta {
        margin-top: 0.35rem;
        color: var(--tp-muted);
        font-size: 0.9rem;
        line-height: 1.45;
    }

    .tp-score {
        flex: 0 0 auto;
        display: inline-block;
        background: #fff0f1;
        color: var(--tp-red-dark);
        border: 1px solid #ffd3d5;
        border-radius: 999px;
        padding: 0.42rem 0.68rem;
        font-weight: 800;
        font-size: 0.82rem;
        white-space: nowrap;
    }

    .tp-facts {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin: 1rem 0 0.9rem 0;
    }

    .tp-fact {
        background: var(--tp-soft);
        border: 1px solid #ececee;
        border-radius: 8px;
        padding: 0.4rem 0.62rem;
        color: #4d5058;
        font-size: 0.82rem;
    }

    .tp-rationale {
        color: #4b4e55;
        line-height: 1.55;
        font-size: 0.92rem;
        margin: 0.2rem 0 1rem 0;
    }

    .tp-rationale b {color: var(--tp-charcoal);}

    .tp-card-link {
        display: inline-block;
        text-decoration: none !important;
        background: var(--tp-charcoal);
        color: #ffffff !important;
        padding: 0.58rem 0.85rem;
        border-radius: 8px;
        font-size: 0.84rem;
        font-weight: 700;
    }

    .tp-card-link:hover {background: var(--tp-red);}

    /* Download button should be secondary */
    .stDownloadButton > button {
        border-radius: 10px !important;
        border: 1px solid var(--tp-charcoal) !important;
        background: #ffffff !important;
        color: var(--tp-charcoal) !important;
        font-weight: 700 !important;
        min-height: 2.8rem;
    }

    .stDownloadButton > button:hover {
        border-color: var(--tp-red) !important;
        color: var(--tp-red) !important;
    }

    .tp-footer {
        margin-top: 2.5rem;
        padding-top: 1.1rem;
        border-top: 1px solid var(--tp-border);
        color: #8a8d94;
        font-size: 0.78rem;
        text-align: center;
    }

    @media (max-width: 720px) {
        .tp-hero {padding: 2.3rem 1.5rem 2.15rem 1.5rem; border-radius: 17px;}
        .tp-brand-label {display: none;}
        .tp-card-top {display: block;}
        .tp-score {margin-top: 0.7rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
@st.cache_data
def load_default_data():
    path = Path("data/program_master.xlsx")
    if path.exists():
        return pd.read_excel(path)
    return pd.DataFrame()


def first_value(row, columns, default=""):
    for col in columns:
        if col in row.index and pd.notna(row[col]) and str(row[col]).strip():
            return row[col]
    return default


def fmt_fee(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    try:
        num = float(str(value).replace(",", "").replace("₹", "").strip())
        if num <= 0:
            return ""
        return f"₹{num:,.0f}"
    except (ValueError, TypeError):
        text = str(value).strip()
        return text


def fmt_duration(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    try:
        num = float(value)
        if num.is_integer():
            return f"{int(num)} months"
        return f"{num:g} months"
    except (ValueError, TypeError):
        return str(value).strip()


def safe(value):
    return html.escape(str(value)) if value is not None else ""


def render_program_card(row):
    score = int(round(float(row.get("_score", 0))))
    name = first_value(row, ["Program Name", "Programme Name"], "Programme")
    institute = first_value(row, ["Institute", "Institute Name"])
    category = first_value(row, ["Program Category", "Programme Category", "Category"])
    vertical = first_value(row, ["Vertical"])
    duration = fmt_duration(first_value(row, ["Duration (Months)", "Duration", "Duration (in months)"]))
    fee = fmt_fee(first_value(row, ["Fee (INR)", "Fee", "Fee (in INR)"]))
    immersion = first_value(row, ["Campus Immersion", "Immersion"])
    link = first_value(row, ["Program Link", "Programme Link", "URL"])
    rationale = row.get("_rationale", "")

    metadata = " · ".join(
        safe(v) for v in [institute, category, vertical] if str(v).strip()
    )

    facts = []
    if duration:
        facts.append(f'<span class="tp-fact"><b>Duration</b>&nbsp; {safe(duration)}</span>')
    if fee:
        facts.append(f'<span class="tp-fact"><b>Fee</b>&nbsp; {safe(fee)}</span>')
    if str(immersion).strip():
        facts.append(f'<span class="tp-fact"><b>Immersion</b>&nbsp; {safe(immersion)}</span>')

    link_html = ""
    if str(link).strip().lower().startswith("http"):
        link_html = (
            f'<a class="tp-card-link" href="{safe(link)}" target="_blank" '
            f'rel="noopener noreferrer">View programme ↗</a>'
        )

    card = f"""
    <div class="tp-program-card">
        <div class="tp-card-accent"></div>
        <div class="tp-card-body">
            <div class="tp-card-top">
                <div>
                    <div class="tp-card-title">{safe(name)}</div>
                    <div class="tp-card-meta">{metadata}</div>
                </div>
                <div class="tp-score">{score}% match</div>
            </div>
            <div class="tp-facts">{''.join(facts)}</div>
            <div class="tp-rationale"><b>Why it fits:</b> {safe(rationale)}</div>
            {link_html}
        </div>
    </div>
    """
    st.markdown(card, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Data
# -----------------------------------------------------------------------------
df = load_default_data()


# -----------------------------------------------------------------------------
# Header and hero
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="tp-brandbar">
        <div class="tp-wordmark">Times<span>Pro</span></div>
        <div class="tp-brand-label">Enterprise Learning Solutions</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="tp-hero">
        <div class="tp-kicker"><span class="tp-kicker-dot"></span> TimesPro for Enterprise</div>
        <h1>Build the right learning portfolio for your workforce.</h1>
        <p>
            Share your organisation's workforce priorities and capability needs.
            We will identify the most relevant TimesPro programmes for your teams.
        </p>
        <div class="tp-hero-tags">
            <span class="tp-hero-tag">Executive Education</span>
            <span class="tp-hero-tag">Management</span>
            <span class="tp-hero-tag">Technology & Engineering</span>
            <span class="tp-hero-tag">Enterprise Capability Building</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if df.empty:
    st.error(
        "Programme master not found. Please ensure `data/program_master.xlsx` exists in the GitHub repository."
    )
    st.stop()


# -----------------------------------------------------------------------------
# Discovery form
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="tp-section-head">
        <div class="tp-section-index">01 · Client requirement</div>
        <h2>Tell us what your organisation needs</h2>
        <p>Use the client context to build a focused, ready-to-discuss learning portfolio.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("discovery_form"):
    c1, c2 = st.columns(2, gap="large")

    with c1:
        company = st.text_input("Organisation name", placeholder="e.g. HDFC Bank")
        industry = st.selectbox(
            "Industry",
            [
                "Banking & Financial Services",
                "Technology / IT & ITES",
                "Manufacturing",
                "Consulting & Professional Services",
                "Retail & E-commerce",
                "Healthcare & Pharma",
                "Energy & Infrastructure",
                "FMCG",
                "Automotive",
                "Telecom",
                "Government / PSU",
                "Other",
            ],
        )
        audience = st.multiselect(
            "Target learner group",
            [
                "Early Career / Individual Contributors",
                "First-time Managers",
                "Mid-level Managers",
                "Senior Leaders",
                "Functional Specialists",
                "CXO / Business Leaders",
            ],
            default=["Mid-level Managers"],
        )
        learner_count = st.selectbox(
            "Approximate learner population",
            ["<25", "25–50", "51–100", "101–250", "251–500", "500+"],
        )

    with c2:
        capability = st.multiselect(
            "Priority capability areas",
            [
                "Leadership & General Management",
                "Artificial Intelligence & GenAI",
                "Data & Analytics",
                "Digital Transformation",
                "Finance & Banking",
                "Sales & Marketing",
                "Operations & Supply Chain",
                "Project / Product Management",
                "HR & People Leadership",
                "Strategy & Business Transformation",
                "Cybersecurity / Cloud / Technology",
                "Sustainability / ESG",
                "Public Policy",
                "Other",
            ],
            default=["Leadership & General Management"],
        )
        business_goal = st.multiselect(
            "Business outcome",
            [
                "Build leadership pipeline",
                "Upskill existing workforce",
                "Reskill for new roles",
                "Drive AI / digital adoption",
                "Improve functional capability",
                "Prepare high-potential talent",
                "Support succession planning",
                "Improve productivity / execution",
                "Create cross-functional business leaders",
            ],
            default=["Upskill existing workforce"],
        )
        mode = st.multiselect(
            "Preferred learning format",
            ["Live Online", "Blended", "On-campus / Immersion", "Self-paced"],
            default=["Live Online", "Blended"],
        )
        duration = st.selectbox(
            "Preferred programme duration",
            ["No preference", "< 3 months", "3–6 months", "6–9 months", "9–12 months", "12+ months"],
        )

    st.markdown("#### Additional context")
    challenge = st.text_area(
        "Describe the capability gap or business challenge",
        placeholder=(
            "Example: We want 50 mid-level BFSI managers to strengthen financial decision-making, "
            "understand emerging FinTech trends and lead cross-functional transformation initiatives."
        ),
        height=110,
    )

    submitted = st.form_submit_button(
        "Find recommended programmes  →",
        type="primary",
        use_container_width=True,
    )


# -----------------------------------------------------------------------------
# Results
# -----------------------------------------------------------------------------
if submitted:
    requirements = {
        "industry": industry,
        "audience": audience,
        "capability": capability,
        "business_goal": business_goal,
        "mode": mode,
        "duration": duration,
        "challenge": challenge,
    }

    results = recommend_programs(df, requirements, top_n=8)

    st.markdown(
        """
        <div class="tp-section-head">
            <div class="tp-section-index">02 · Recommended portfolio</div>
            <h2>Recommended learning portfolio</h2>
            <p>Programmes are ranked primarily on industry and capability relevance, followed by learner seniority and business outcome.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    org = company.strip() if company.strip() else "Your organisation"
    aud = ", ".join(audience) if audience else "Multiple learner groups"
    cap = ", ".join(capability) if capability else "Multiple capabilities"

    st.markdown(
        f"""
        <div class="tp-results-banner">
            <strong>{safe(org)}</strong><br>
            <span>{safe(industry)} &nbsp;•&nbsp; {safe(aud)} &nbsp;•&nbsp; {safe(cap)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if results.empty:
        st.warning(
            "No sufficiently relevant programmes were found for these criteria. "
            "Try broadening the capability area or learner profile."
        )
    else:
        for _, row in results.iterrows():
            render_program_card(row)

        visible_cols = [c for c in results.columns if not c.startswith("_")]
        csv = results[visible_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download recommended portfolio",
            data=csv,
            file_name="timespro_enterprise_recommendations.csv",
            mime="text/csv",
            use_container_width=True,
        )


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="tp-footer">
        TimesPro Enterprise Learning Solutions · Recommendation prototype for B2B solutioning.<br>
        Programme recommendations should be validated by the TimesPro team before external sharing.<br>
        <span style="font-size:0.75rem;color:#9ca3af;">Recommendation engine v{MATCHER_VERSION}</span>
    </div>
    """,
    unsafe_allow_html=True,
)
