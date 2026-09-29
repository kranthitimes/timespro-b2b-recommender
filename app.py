import streamlit as st
import pandas as pd
from pathlib import Path

try:
    from matcher import recommend_programs, MATCHER_VERSION
except ImportError:
    from matcher import recommend_programs
    MATCHER_VERSION = "unknown"

# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="TimesPro B2B Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# Simple, consistent light UI
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        /* Page */
        .stApp {
            background: #FFFFFF;
            color: #222222;
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* Hide Streamlit chrome for a cleaner client-facing view */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* Typography */
        h1, h2, h3 {
            color: #222222 !important;
            font-weight: 650 !important;
        }

        p, label, .stMarkdown {
            color: #4B5563;
        }

        /* Inputs - force readable light theme in all browsers */
        input,
        textarea {
            color: #222222 !important;
            background-color: #FFFFFF !important;
            -webkit-text-fill-color: #222222 !important;
            opacity: 1 !important;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #222222 !important;
            border-color: #D1D5DB !important;
        }

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {
            color: #222222 !important;
        }

        /* Multiselect tags */
        span[data-baseweb="tag"] {
            background-color: #FEE2E2 !important;
            color: #B91C1C !important;
            border: none !important;
        }

        span[data-baseweb="tag"] * {
            color: #B91C1C !important;
        }

        /* Form */
        div[data-testid="stForm"] {
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 1.4rem 1.4rem 0.7rem 1.4rem;
            background: #FFFFFF;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }

        /* Buttons */
        div.stButton > button,
        div.stFormSubmitButton > button {
            background: #E31E24 !important;
            color: #FFFFFF !important;
            border: 1px solid #E31E24 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            min-height: 44px;
        }

        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {
            background: #C8171C !important;
            border-color: #C8171C !important;
        }

        /* Download button */
        div.stDownloadButton > button {
            background: #FFFFFF !important;
            color: #222222 !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 8px !important;
        }

        /* Client context */
        .client-summary {
            background: #FAFAFA;
            border: 1px solid #E5E7EB;
            border-left: 4px solid #E31E24;
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin: 1rem 0 1.5rem 0;
        }

        /* Small brand kicker */
        .brand-kicker {
            color: #E31E24;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .subtle {
            color: #6B7280;
            font-size: 0.95rem;
        }

        /* Result card */
        .program-card {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 1.25rem 1.35rem;
            margin-bottom: 1rem;
            background: #FFFFFF;
        }

        .program-title {
            color: #222222;
            font-size: 1.2rem;
            font-weight: 650;
            margin-bottom: 0.25rem;
        }

        .program-meta {
            color: #6B7280;
            font-size: 0.9rem;
            margin-bottom: 0.9rem;
        }

        .match-pill {
            display: inline-block;
            background: #FEF2F2;
            color: #B91C1C;
            border: 1px solid #FECACA;
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .detail-pill {
            display: inline-block;
            background: #F9FAFB;
            color: #4B5563;
            border: 1px solid #E5E7EB;
            border-radius: 7px;
            padding: 0.35rem 0.55rem;
            margin-right: 0.35rem;
            margin-bottom: 0.45rem;
            font-size: 0.84rem;
        }

        /* Prevent dark-mode injected text colors */
        [data-testid="stWidgetLabel"] p {
            color: #374151 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
brand_icon = Path("assets/timespro_app_icon.png")

if brand_icon.exists():
    icon_col, text_col = st.columns([1, 10], vertical_alignment="center")
    with icon_col:
        st.image(str(brand_icon), width=72)
    with text_col:
        st.markdown('<div class="brand-kicker">TimesPro Enterprise</div>', unsafe_allow_html=True)
        st.title("Learning Programme Recommender")
else:
    st.markdown('<div class="brand-kicker">TimesPro Enterprise</div>', unsafe_allow_html=True)
    st.title("Learning Programme Recommender")

st.markdown(
    '<div class="subtle">Identify relevant TimesPro programmes based on your client’s industry, workforce profile and capability priorities.</div>',
    unsafe_allow_html=True,
)

st.write("")

# ---------------------------------------------------------
# Requirements form
# ---------------------------------------------------------
st.subheader("Tell us what your organisation needs")
st.caption("Enter the client context below. Only the most relevant fields are required.")

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
        placeholder="Optional: e.g. Build stronger financial decision-making capability among mid-level managers.",
        height=95,
    )

    submitted = st.form_submit_button(
        "Find recommended programmes",
        type="primary",
        use_container_width=True,
    )

# ---------------------------------------------------------
# Results
# ---------------------------------------------------------
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
        st.markdown('<div class="brand-kicker">Recommended portfolio</div>', unsafe_allow_html=True)
        st.header("Recommended learning portfolio")
        st.caption(
            "Programmes are ranked using capability relevance first, followed by industry, learner profile and business outcome."
        )

        context_bits = [industry]
        if audience:
            context_bits.append(", ".join(audience))
        if capability:
            context_bits.append(", ".join(capability))

        st.markdown(
            f"""
            <div class="client-summary">
                <strong>{company or "Client organisation"}</strong><br>
                <span style="color:#6B7280;">{" • ".join(context_bits)}</span>
            </div>
            """,
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
                category = first_value(row, ["Program Category", "Programme Category", "Category"], "")
                vertical = first_value(row, ["Vertical"], "")
                duration_val = first_value(row, ["Duration", "Duration (Months)", "Duration (in months)"], "")
                fee_val = first_value(row, ["Fee", "Fee (INR)", "Fee (in INR)"], "")
                immersion = first_value(row, ["Immersion", "Campus Immersion"], "")
                link = first_value(row, ["Program Link", "Programme Link", "URL"], "")
                score = int(row.get("_score", 0))
                rationale = row.get("_rationale", "")

                metadata = " · ".join(
                    [str(x) for x in [institute, category, vertical] if str(x).strip()]
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
                    detail_html += f'<span class="detail-pill">Duration&nbsp; {format_duration(duration_val)}</span>'
                if str(fee_val).strip():
                    detail_html += f'<span class="detail-pill">Fee&nbsp; {format_fee(fee_val)}</span>'

                if detail_html:
                    st.markdown(detail_html, unsafe_allow_html=True)

                if str(immersion).strip() and str(immersion).lower() not in ["nan", "no", "none"]:
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
