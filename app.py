
import streamlit as st
import pandas as pd
from pathlib import Path
from matcher import recommend_programs

st.set_page_config(
    page_title="TimesPro Enterprise Learning Solutions",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
    .block-container {padding-top: 1.5rem; max-width: 1250px;}
    .hero {
        padding: 3rem 3rem 2.5rem 3rem;
        border-radius: 22px;
        background: linear-gradient(120deg, #111827 0%, #1f2937 62%, #374151 100%);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 {font-size: 3rem; line-height: 1.05; margin-bottom: .8rem;}
    .hero p {font-size: 1.15rem; max-width: 820px; color: #e5e7eb;}
    .eyebrow {
        font-size: .8rem;
        text-transform: uppercase;
        letter-spacing: .12rem;
        font-weight: 700;
        color: #9ca3af;
        margin-bottom: .5rem;
    }
    .card {
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.15rem 1.2rem;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 3px 14px rgba(0,0,0,.04);
    }
    .score {
        display: inline-block;
        padding: .25rem .55rem;
        border-radius: 999px;
        background: #eef2ff;
        font-size: .82rem;
        font-weight: 700;
    }
    .muted {color: #6b7280;}
    .footer-note {font-size: .83rem; color: #6b7280;}
    div[data-testid="stForm"] {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1.3rem 1.4rem .5rem 1.4rem;
        background: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Data loading
# -----------------------------
@st.cache_data
def load_default_data():
    p = Path("data/program_master.xlsx")
    if p.exists():
        return pd.read_excel(p)
    return pd.DataFrame()

df = load_default_data()

# -----------------------------
# Hero
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="eyebrow">TimesPro for Enterprise</div>
    <h1>Build the right learning portfolio for your workforce.</h1>
    <p>
        Tell us about your organisation, workforce priorities and capability needs.
        We will identify the most relevant TimesPro programmes for your teams.
    </p>
</div>
""", unsafe_allow_html=True)

# Optional master data upload for demo / admin testing
with st.expander("Admin / Demo: load programme master"):
    uploaded = st.file_uploader(
        "Upload TimesPro programme master (.xlsx)",
        type=["xlsx"],
        help="In production, keep the master Excel in the GitHub repo or connect it to a managed source."
    )
    if uploaded:
        df = pd.read_excel(uploaded)
        st.success(f"Loaded {len(df)} programmes.")

if df.empty:
    st.info(
        "No programme master is loaded yet. Add `data/program_master.xlsx` to the repo "
        "or upload an Excel above. The interface is ready for the TimesPro dataset."
    )

# -----------------------------
# Discovery form
# -----------------------------
st.subheader("Tell us what your organisation needs")

with st.form("discovery_form"):
    c1, c2 = st.columns(2)

    with c1:
        company = st.text_input("Organisation name")
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
                "Other"
            ]
        )
        audience = st.multiselect(
            "Target learner group",
            [
                "Early Career / Individual Contributors",
                "First-time Managers",
                "Mid-level Managers",
                "Senior Leaders",
                "Functional Specialists",
                "CXO / Business Leaders"
            ],
            default=["Mid-level Managers"]
        )
        learner_count = st.selectbox(
            "Approximate learner population",
            ["<25", "25–50", "51–100", "101–250", "251–500", "500+"]
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
                "Other"
            ],
            default=["Leadership & General Management"]
        )
        business_goal = st.multiselect(
            "What business outcome are you targeting?",
            [
                "Build leadership pipeline",
                "Upskill existing workforce",
                "Reskill for new roles",
                "Drive AI / digital adoption",
                "Improve functional capability",
                "Prepare high-potential talent",
                "Support succession planning",
                "Improve productivity / execution",
                "Create cross-functional business leaders"
            ],
            default=["Upskill existing workforce"]
        )
        mode = st.multiselect(
            "Preferred learning format",
            ["Live Online", "Blended", "On-campus / Immersion", "Self-paced"],
            default=["Live Online", "Blended"]
        )
        duration = st.selectbox(
            "Preferred programme duration",
            ["No preference", "< 3 months", "3–6 months", "6–9 months", "9–12 months", "12+ months"]
        )

    st.markdown("#### Additional context")
    challenge = st.text_area(
        "Describe the capability gap or business challenge",
        placeholder="Example: We want 50 mid-level BFSI managers to understand GenAI use cases, lead transformation projects and manage cross-functional teams."
    )

    submitted = st.form_submit_button("Find recommended programmes", type="primary", use_container_width=True)

# -----------------------------
# Results
# -----------------------------
if submitted:
    if df.empty:
        st.warning("Please load the TimesPro programme master to generate recommendations.")
    else:
        requirements = {
            "industry": industry,
            "audience": audience,
            "capability": capability,
            "business_goal": business_goal,
            "mode": mode,
            "duration": duration,
            "challenge": challenge
        }

        results = recommend_programs(df, requirements, top_n=8)

        st.divider()
        st.markdown("## Recommended learning portfolio")
        st.caption(
            f"For {company or 'your organisation'} · {industry} · "
            f"{', '.join(audience) if audience else 'Multiple learner groups'}"
        )

        if results.empty:
            st.info("No strong matches were found. Broaden the requirements or improve programme tags in the master.")
        else:
            # Executive summary
            top_categories = (
                results["Program Category"].dropna().astype(str).value_counts().head(3).index.tolist()
                if "Program Category" in results.columns else []
            )
            if top_categories:
                st.write(
                    "**Portfolio direction:** The strongest matches cluster around "
                    + ", ".join(top_categories)
                    + "."
                )

            for i, row in results.iterrows():
                score = int(row.get("_score", 0))
                name = row.get("Program Name", "Programme")
                institute = row.get("Institute Name", "")
                category = row.get("Program Category", "")
                duration_val = row.get("Duration (Months)", row.get("Duration", row.get("Duration (in months)", "")))
                fee = row.get("Fee (INR)", row.get("Fee", row.get("Fee (in INR)", "")))
                mode_val = row.get("Mode", "")
                link = row.get("Program Link", "")
                rationale = row.get("_rationale", "")

                st.markdown('<div class="card">', unsafe_allow_html=True)
                a, b = st.columns([5, 1])
                with a:
                    st.markdown(f"### {name}")
                    meta = " · ".join([str(x) for x in [institute, category] if pd.notna(x) and str(x).strip()])
                    if meta:
                        st.markdown(f'<span class="muted">{meta}</span>', unsafe_allow_html=True)
                with b:
                    st.markdown(f'<span class="score">{score}% match</span>', unsafe_allow_html=True)

                bits = []
                if pd.notna(duration_val) and str(duration_val).strip():
                    bits.append(f"**Duration:** {duration_val}")
                if pd.notna(mode_val) and str(mode_val).strip():
                    bits.append(f"**Mode:** {mode_val}")
                if pd.notna(fee) and str(fee).strip():
                    bits.append(f"**Fee:** {fee}")
                if bits:
                    st.write(" | ".join(bits))

                if rationale:
                    st.write(f"**Why it fits:** {rationale}")

                if pd.notna(link) and str(link).startswith("http"):
                    st.link_button("View programme", str(link))

                st.markdown("</div>", unsafe_allow_html=True)

            # Download/shareable shortlist
            visible_cols = [c for c in results.columns if not c.startswith("_")]
            csv = results[visible_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download shortlist as CSV",
                csv,
                "timespro_enterprise_recommendations.csv",
                "text/csv",
                use_container_width=True
            )

st.divider()
st.markdown(
    '<div class="footer-note">Prototype recommendation engine. Final recommendations should be validated by the TimesPro B2B/Product team before being shared externally.</div>',
    unsafe_allow_html=True
)
