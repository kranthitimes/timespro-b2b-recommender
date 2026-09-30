import streamlit as st
import pandas as pd
from pathlib import Path

try:
    from matcher import recommend_programs, MATCHER_VERSION
except ImportError:
    from matcher import recommend_programs
    MATCHER_VERSION = "unknown"

st.set_page_config(
    page_title="TimesPro B2B Recommender",
    page_icon=".assets/ChatGPT Image Sep 29, 2026, 03_09_12 PM.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.stMarkdown,
input,
textarea,
button,
select {
    font-family: 'Montserrat', sans-serif !important;
}

/* Main page title */
h1 {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
    font-size: 2.15rem !important;
    line-height: 1.15 !important;
    letter-spacing: -0.03em !important;
    color: #222222 !important;
}

/* Section headings */
h2 {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.55rem !important;
    line-height: 1.25 !important;
    letter-spacing: -0.02em !important;
    color: #222222 !important;
}

/* Smaller headings */
h3, h4 {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    color: #222222 !important;
}

/* Body copy */
p,
.stMarkdown,
.stCaption {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 400 !important;
    line-height: 1.55 !important;
}

/* Form labels */
[data-testid="stWidgetLabel"] p {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
}

/* Input / dropdown text */
input,
textarea,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 400 !important;
    font-size: 0.93rem !important;
}

/* Multiselect tags */
span[data-baseweb="tag"] {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
}

/* Primary and secondary buttons */
div.stButton > button,
div.stFormSubmitButton > button,
div.stDownloadButton > button,
div[data-testid="stLinkButton"] a {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

/* TimesPro eyebrow label */
.brand-kicker {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.11em;
    text-transform: uppercase;
}

/* Intro / secondary text */
.subtle {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.94rem;
    font-weight: 400;
    line-height: 1.55;
}

/* Programme result title */
.program-title {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 1.12rem;
    font-weight: 600;
    line-height: 1.35;
    color: #222222;
}

/* Programme metadata */
.program-meta {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.84rem;
    font-weight: 400;
    color: #6B7280;
}

/* Match badge */
.match-pill {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.78rem;
    font-weight: 600;
}

/* Duration / fee pills */
.detail-pill {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.8rem;
    font-weight: 500;
}
        :root {
            --tp-red: #E31E24;
            --tp-red-dark: #C8171C;
            --tp-red-soft: #FEF2F2;
            --tp-text: #222222;
            --tp-body: #4B5563;
            --tp-muted: #6B7280;
            --tp-border: #E5E7EB;
            --tp-surface: #F8F9FA;
            --tp-white: #FFFFFF;
        }

        .stApp {
            background: var(--tp-white);
            color: var(--tp-text);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {background: transparent;}

        h1, h2, h3, h4 { color: var(--tp-text) !important; }
        h1 { font-weight: 700 !important; letter-spacing: -0.02em; }
        h2, h3 { font-weight: 650 !important; }

        p, label, .stMarkdown { color: var(--tp-body); }

        .brand-kicker {
            color: var(--tp-red);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .subtle {
            color: var(--tp-muted);
            font-size: 0.97rem;
            line-height: 1.55;
        }

        .brand-line {
            width: 58px;
            height: 4px;
            background-color: var(--tp-red);
            border-radius: 999px;
            margin: 0.9rem 0 1.6rem 0;
        }

        div[data-testid="stForm"] {
            border: 1px solid var(--tp-border);
            border-radius: 14px;
            padding: 1.45rem 1.45rem 0.9rem 1.45rem;
            background: var(--tp-white);
            box-shadow: 0 4px 18px rgba(0,0,0,0.04);
        }

        [data-testid="stWidgetLabel"] p {
            color: #374151 !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
        }

        input, textarea {
            color: var(--tp-text) !important;
            background-color: var(--tp-white) !important;
            -webkit-text-fill-color: var(--tp-text) !important;
            opacity: 1 !important;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div {
            background-color: var(--tp-white) !important;
            color: var(--tp-text) !important;
            border: 1px solid #D9DDE3 !important;
            border-radius: 8px !important;
        }

        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within {
            border-color: var(--tp-red) !important;
            box-shadow: 0 0 0 1px var(--tp-red) !important;
        }

        div[data-baseweb="select"] > div {
            background-color: var(--tp-surface) !important;
            color: var(--tp-text) !important;
            border: 1px solid #D9DDE3 !important;
            border-radius: 8px !important;
            min-height: 46px;
        }

        div[data-baseweb="select"] > div:hover {
            border-color: #B8BDC6 !important;
        }

        div[data-baseweb="select"] > div:focus-within {
            border-color: var(--tp-red) !important;
            box-shadow: 0 0 0 1px var(--tp-red) !important;
        }

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {
            color: var(--tp-text) !important;
        }

        span[data-baseweb="tag"] {
            background-color: var(--tp-red-soft) !important;
            color: #B91C1C !important;
            border: 1px solid #FECACA !important;
            border-radius: 6px !important;
        }

        span[data-baseweb="tag"] * {
            color: #B91C1C !important;
        }

        div.stButton > button,
        div.stFormSubmitButton > button {
            background-color: var(--tp-red) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--tp-red) !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            min-height: 48px !important;
            box-shadow: none !important;
        }

        div.stButton > button p,
        div.stButton > button span,
        div.stFormSubmitButton > button p,
        div.stFormSubmitButton > button span {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {
            background-color: var(--tp-red-dark) !important;
            border-color: var(--tp-red-dark) !important;
        }

        div.stDownloadButton > button,
        div[data-testid="stLinkButton"] a {
            background: var(--tp-white) !important;
            color: var(--tp-text) !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }

        div.stDownloadButton > button p,
        div[data-testid="stLinkButton"] a p,
        div[data-testid="stLinkButton"] a span {
            color: var(--tp-text) !important;
        }

        .client-summary {
            background: #FAFAFA;
            border: 1px solid var(--tp-border);
            border-left: 4px solid var(--tp-red);
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin: 1rem 0 1.5rem 0;
        }

        .program-card {
            border: 1px solid var(--tp-border);
            border-radius: 12px;
            padding: 1.35rem 1.4rem;
            margin-bottom: 1rem;
            background: var(--tp-white);
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }

        .program-title {
            color: var(--tp-text);
            font-size: 1.18rem;
            font-weight: 700;
            margin-bottom: 0.28rem;
        }

        .program-meta {
            color: var(--tp-muted);
            font-size: 0.9rem;
            margin-bottom: 0.9rem;
        }

        .match-pill {
            display: inline-block;
            background: var(--tp-red-soft);
            color: #B91C1C;
            border: 1px solid #FECACA;
            border-radius: 999px;
            padding: 0.3rem 0.68rem;
            font-size: 0.8rem;
            font-weight: 800;
            white-space: nowrap;
        }

        .detail-pill {
            display: inline-block;
            background: #F9FAFB;
            color: var(--tp-body);
            border: 1px solid var(--tp-border);
            border-radius: 6px;
            padding: 0.35rem 0.55rem;
            margin-right: 0.4rem;
            margin-bottom: 0.45rem;
            font-size: 0.82rem;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
    </style>
    ''',
    unsafe_allow_html=True,
)

@st.cache_data
def load_program_data():
    path = Path("data/program_master.xlsx")
    if path.exists():
        return pd.read_excel(path)
    return pd.DataFrame()

def first_value(row, columns, default=""):
    for col in columns:
        if col in row.index and pd.notna(row[col]) and str(row[col]).strip():
            return row[col]
    return default

def format_fee(value):
    if value is None or pd.isna(value) or str(value).strip() == "":
        return ""
    try:
        number = float(str(value).replace(",", "").replace("₹", "").strip())
        return f"₹{number:,.0f}"
    except Exception:
        return str(value)

def format_duration(value):
    if value is None or pd.isna(value) or str(value).strip() == "":
        return ""
    text = str(value).strip()
    if text.replace(".", "", 1).isdigit():
        number = float(text)
        if number.is_integer():
            return f"{int(number)} months"
        return f"{number:g} months"
    return text

df = load_program_data()

brand_icon = Path(".assets/timespro_logo.png")

if brand_icon.exists():
    logo_col, title_col = st.columns([1, 8], vertical_alignment="center")

    with logo_col:
        st.image(str(brand_icon), width=90)

    with title_col:
        st.markdown(
            '<div class="brand-kicker">TimesPro Enterprise</div>',
            unsafe_allow_html=True,
        )
        st.title("Executive Education Programme Recommendation Tool")
else:
    st.markdown(
        '<div class="brand-kicker">TimesPro Enterprise</div>',
        unsafe_allow_html=True,
    )
    st.title("Executive Education Programme Recommendation Tool")

st.markdown(
    '''
    <div class="subtle">
        Match organisational capability requirements with relevant TimesPro programmes
        from leading institutions.
    </div>
    ''',
    unsafe_allow_html=True,
)

st.markdown('<div class="brand-line"></div>', unsafe_allow_html=True)

st.subheader("Tell us what your organisation needs")
st.caption("Enter the client context below to build a focused learning portfolio.")

with st.form("discovery_form"):
    left, right = st.columns(2, gap="large")

    with left:
        company = st.text_input(
            "Organisation name",
            placeholder="e.g. HDFC Bank",
        )

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

    with right:
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
            [
                "No preference",
                "< 3 months",
                "3–6 months",
                "6–9 months",
                "9–12 months",
                "12+ months",
            ],
        )

    st.markdown("#### Additional context")

    challenge = st.text_area(
        "Capability gap or business challenge",
        placeholder=(
            "Optional: e.g. Build stronger financial decision-making capability "
            "among mid-level managers."
        ),
        height=95,
    )

    submitted = st.form_submit_button(
        "Find recommended programmes",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if df.empty:
        st.error("Programme master not found. Please check `data/program_master.xlsx`.")
    elif not capability:
        st.warning("Please select at least one priority capability area.")
    else:
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

        st.write("")
        st.markdown(
            '<div class="brand-kicker">Recommended portfolio</div>',
            unsafe_allow_html=True,
        )
        st.header("Recommended learning portfolio")
        st.caption(
            "Programmes are ranked primarily by capability relevance, followed by "
            "industry, learner profile and business outcome."
        )

        context_bits = [industry]
        if audience:
            context_bits.append(", ".join(audience))
        if capability:
            context_bits.append(", ".join(capability))

        st.markdown(
            f'''
            <div class="client-summary">
                <strong>{company or "Client organisation"}</strong><br>
                <span style="color:#6B7280;">{" • ".join(context_bits)}</span>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        if results.empty:
            st.info(
                "No strong programme matches were found for this combination. "
                "Try broadening the capability, duration or learner profile."
            )
        else:
            for _, row in results.iterrows():
                name = first_value(row, ["Program Name", "Programme Name"], "Programme")
                institute = first_value(row, ["Institute Name", "Institute"], "")
                category = first_value(
                    row,
                    ["Program Category", "Programme Category", "Category"],
                    "",
                )
                vertical = first_value(row, ["Vertical"], "")
                duration_val = first_value(
                    row,
                    ["Duration", "Duration (Months)", "Duration (in months)"],
                    "",
                )
                fee_val = first_value(
                    row,
                    ["Fee", "Fee (INR)", "Fee (in INR)"],
                    "",
                )
                immersion = first_value(
                    row,
                    ["Immersion", "Campus Immersion"],
                    "",
                )
                link = first_value(
                    row,
                    ["Program Link", "Programme Link", "URL"],
                    "",
                )
                score = int(row.get("_score", 0))
                rationale = row.get("_rationale", "")

                metadata = " · ".join(
                    [
                        str(x)
                        for x in [institute, category, vertical]
                        if str(x).strip()
                    ]
                )

                st.markdown('<div class="program-card">', unsafe_allow_html=True)

                title_col, score_col = st.columns([7, 1])

                with title_col:
                    st.markdown(
                        f'<div class="program-title">{name}</div>',
                        unsafe_allow_html=True,
                    )

                    if metadata:
                        st.markdown(
                            f'<div class="program-meta">{metadata}</div>',
                            unsafe_allow_html=True,
                        )

                with score_col:
                    st.markdown(
                        f'<span class="match-pill">{score}% match</span>',
                        unsafe_allow_html=True,
                    )

                detail_html = ""

                if str(duration_val).strip():
                    detail_html += (
                        f'<span class="detail-pill">'
                        f'Duration&nbsp; {format_duration(duration_val)}'
                        f'</span>'
                    )

                if str(fee_val).strip():
                    detail_html += (
                        f'<span class="detail-pill">'
                        f'Fee&nbsp; {format_fee(fee_val)}'
                        f'</span>'
                    )

                if detail_html:
                    st.markdown(detail_html, unsafe_allow_html=True)

                if (
                    str(immersion).strip()
                    and str(immersion).lower() not in ["nan", "no", "none"]
                ):
                    st.caption(f"Immersion: {immersion}")

                if rationale:
                    st.markdown(f"**Why it fits:** {rationale}")

                if str(link).startswith("http"):
                    st.link_button("View programme", str(link))

                st.markdown("</div>", unsafe_allow_html=True)

            visible_cols = [c for c in results.columns if not c.startswith("_")]
            csv = results[visible_cols].to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download recommendation shortlist",
                data=csv,
                file_name="timespro_programme_recommendations.csv",
                mime="text/csv",
                use_container_width=True,
            )

st.write("")
st.caption(f"Recommendation engine v{MATCHER_VERSION}")
