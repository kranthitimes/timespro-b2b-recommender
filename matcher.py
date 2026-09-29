import re
import pandas as pd

MATCHER_VERSION = "3.0"

# -----------------------------------------------------------------------------
# Query vocabulary
# -----------------------------------------------------------------------------
INDUSTRY_ALIASES = {
    "banking & financial services": [
        "bfsi", "banking", "financial services", "fintech", "nbfc", "insurance",
        "capital markets", "investment banking", "wealth management", "asset management"
    ],
    "technology / it & ites": ["technology", "it", "ites", "software", "saas", "tech"],
    "manufacturing": ["manufacturing", "industrial", "factory", "production"],
    "consulting & professional services": ["consulting", "professional services", "advisory"],
    "retail & e-commerce": ["retail", "e-commerce", "ecommerce", "digital commerce"],
    "healthcare & pharma": ["healthcare", "pharma", "pharmaceutical", "hospital", "life sciences"],
    "energy & infrastructure": ["energy", "infrastructure", "power", "oil", "gas", "utilities"],
    "fmcg": ["fmcg", "consumer goods", "consumer products"],
    "automotive": ["automotive", "automobile", "mobility", "electric vehicle"],
    "telecom": ["telecom", "telecommunications"],
    "government / psu": ["government", "psu", "public sector", "public administration"],
}

CAPABILITY_ALIASES = {
    "finance & banking": [
        "finance", "financial", "banking", "fintech", "cfo", "capital markets",
        "investment banking", "credit", "risk management", "wealth management",
        "treasury", "valuation", "corporate finance", "quantitative finance"
    ],
    "leadership & general management": [
        "leadership", "general management", "executive management", "business management",
        "strategic leadership", "people leadership"
    ],
    "artificial intelligence & genai": [
        "artificial intelligence", "genai", "generative ai", "machine learning", "agentic ai",
        "ai for business", "ai for leaders"
    ],
    "data & analytics": ["data analytics", "business analytics", "data science", "analytics"],
    "digital transformation": ["digital transformation", "digital strategy", "digital business"],
    "sales & marketing": ["sales", "marketing", "brand", "digital marketing", "customer experience"],
    "operations & supply chain": ["operations", "supply chain", "logistics", "procurement"],
    "project / product management": ["project management", "product management", "product leadership", "agile"],
    "hr & people leadership": ["human resources", "hr", "chro", "talent management", "people management"],
    "strategy & business transformation": ["strategy", "business transformation", "corporate strategy", "geopolitics"],
    "cybersecurity / cloud / technology": ["cybersecurity", "cyber security", "cloud", "technology management"],
    "sustainability / esg": ["sustainability", "esg", "climate", "green"],
    "public policy": ["public policy", "governance", "public administration"],
}

# Terms used to identify the programme's PRIMARY domain.  These deliberately
# look only at programme name + category, which prevents broad auto-tags from
# making unrelated programmes appear relevant.
PRIMARY_DOMAIN_TERMS = {
    "finance & banking": [
        "finance", "financial", "banking", "fintech", "cfo", "capital market",
        "investment banking", "credit", "wealth", "treasury", "valuation",
        "quantitative finance", "risk"
    ],
    "leadership & general management": [
        "general management", "business management", "leadership", "cxO leadership".lower(),
        "executive management", "management development"
    ],
    "artificial intelligence & genai": [
        "artificial intelligence", "generative ai", "gen ai", "genai", "agentic ai", "ai and gen ai", "ai & genai"
    ],
    "data & analytics": ["data science", "data analytics", "business analytics", "analytics"],
    "digital transformation": ["digital transformation", "digital strategy", "digital business"],
    "sales & marketing": ["marketing", "brand", "sales", "customer experience"],
    "operations & supply chain": ["supply chain", "operations", "logistics", "procurement"],
    "project / product management": ["project management", "product management", "product leadership"],
    "hr & people leadership": ["human resources", "hr management", "chro", "people management", "talent management"],
    "strategy & business transformation": ["strategy", "strategic management", "geopolitics", "business transformation"],
    "cybersecurity / cloud / technology": ["cybersecurity", "cyber security", "cloud", "technology management"],
    "sustainability / esg": ["sustainability", "esg", "climate"],
    "public policy": ["public policy", "public administration", "governance"],
}

SENIORITY_ALIASES = {
    "early career / individual contributors": ["early career", "individual contributor", "young professional", "entry level"],
    "first-time managers": ["first-time manager", "new manager", "team lead"],
    "mid-level managers": ["mid-level", "mid level", "middle management", "manager", "5+ years", "6+ years", "7+ years", "8+ years"],
    "senior leaders": ["senior leader", "senior management", "10+ years", "12+ years", "15+ years", "business head", "functional head"],
    "functional specialists": ["specialist", "domain expert", "functional professional"],
    "cxo / business leaders": ["cxo", "chief", "ceo", "cfo", "chro", "cto", "cio", "business leader", "senior executive"],
}

BUSINESS_OUTCOME_ALIASES = {
    "build leadership pipeline": ["leadership pipeline", "future leaders", "leadership development"],
    "upskill existing workforce": ["upskill", "capability building", "skill development", "professional development"],
    "reskill for new roles": ["reskill", "career transition", "role transition"],
    "drive ai / digital adoption": ["ai adoption", "digital adoption", "digital transformation", "genai"],
    "improve functional capability": ["functional capability", "domain capability", "functional expertise"],
    "prepare high-potential talent": ["high potential", "hipo", "future leader"],
    "support succession planning": ["succession", "leadership pipeline"],
    "improve productivity / execution": ["productivity", "execution", "operational excellence"],
    "create cross-functional business leaders": ["cross-functional", "general management", "business leadership"],
}


def _clean(v):
    if pd.isna(v):
        return ""
    return str(v).strip().lower()


def _text(row, columns):
    vals = []
    for col in columns:
        if col in row.index and pd.notna(row[col]):
            vals.append(str(row[col]))
    return " | ".join(vals).lower()


def _has(text, terms):
    text = _clean(text)
    hits = []
    for term in terms:
        term = _clean(term)
        if term and term in text:
            hits.append(term)
    return bool(hits), list(dict.fromkeys(hits))


def _expanded(values, mapping):
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    out = []
    for value in values:
        key = _clean(value)
        out.append(key)
        out.extend(mapping.get(key, []))
    return list(dict.fromkeys([_clean(x) for x in out if _clean(x)]))


def _primary_capability_match(row, selected_capabilities):
    """Match capability against programme name/category only."""
    primary_text = _text(row, ["Program Name", "Programme Name", "Program Category", "Programme Category", "Category"])
    matched_labels = []
    for cap in selected_capabilities or []:
        key = _clean(cap)
        terms = PRIMARY_DOMAIN_TERMS.get(key, [key])
        hit, _ = _has(primary_text, terms)
        if hit:
            matched_labels.append(cap)
    return bool(matched_labels), matched_labels


def _duration_match(value, requested):
    if not requested or requested == "No preference":
        return False
    nums = re.findall(r"\d+(?:\.\d+)?", _clean(value))
    if not nums:
        return False
    months = float(nums[0])
    req = requested.replace("–", "-")
    if "< 3" in req:
        return months < 3
    if "3-6" in req:
        return 3 <= months <= 6
    if "6-9" in req:
        return 6 <= months <= 9
    if "9-12" in req:
        return 9 <= months <= 12
    if "12+" in req:
        return months >= 12
    return False


def recommend_programs(df, requirements, top_n=8):
    """
    TimesPro B2B recommendation engine v3.0.

    Key principle:
    When the buyer explicitly chooses a capability, PRIMARY capability relevance
    (programme name/category) is mandatory. This prevents programmes such as
    Healthcare Management from appearing for Finance & Banking simply because
    the learner seniority matches.
    """
    data = df.copy()

    industry_q = requirements.get("industry", "")
    capabilities_q = requirements.get("capability", []) or []
    audience_q = requirements.get("audience", []) or []
    outcomes_q = requirements.get("business_goal", []) or []
    modes_q = requirements.get("mode", []) or []
    duration_q = requirements.get("duration", "")
    challenge_q = requirements.get("challenge", "")

    industry_terms = _expanded(industry_q, INDUSTRY_ALIASES)
    capability_terms = _expanded(capabilities_q, CAPABILITY_ALIASES)
    audience_terms = _expanded(audience_q, SENIORITY_ALIASES)
    outcome_terms = _expanded(outcomes_q, BUSINESS_OUTCOME_ALIASES)
    mode_terms = [_clean(x) for x in modes_q]

    rows = []

    for _, row in data.iterrows():
        primary_cap_hit, primary_cap_labels = _primary_capability_match(row, capabilities_q)

        industry_text = _text(row, [
            "Industry Tags", "Industry", "Relevant Industries", "Program Name", "Program Category"
        ])
        capability_support_text = _text(row, [
            "Capability Tags", "Program Name", "Program Category", "Target Audience"
        ])
        audience_text = _text(row, [
            "Seniority Tags", "Target Audience", "Work Experience", "Eligibility"
        ])
        outcome_text = _text(row, [
            "Business Outcome Tags", "Target Audience", "Program Name", "Program Category"
        ])
        mode_text = _text(row, ["Mode", "Delivery Mode", "Learning Format"])
        duration_text = _text(row, ["Duration (Months)", "Duration", "Duration (in months)"])

        industry_hit, _ = _has(industry_text, industry_terms)
        supporting_cap_hit, _ = _has(capability_support_text, capability_terms)
        audience_hit, _ = _has(audience_text, audience_terms)
        outcome_hit, _ = _has(outcome_text, outcome_terms)
        mode_hit, _ = _has(mode_text, mode_terms)
        duration_hit = _duration_match(duration_text, duration_q)

        # HARD GATE: explicit capability selection requires genuine primary-domain fit.
        if capabilities_q and not primary_cap_hit:
            continue

        # If no capability was selected, at least industry relevance is needed.
        if not capabilities_q and industry_q and not industry_hit:
            continue

        score = 0.0
        reasons = []

        # Primary capability is the dominant factor.
        if primary_cap_hit:
            score += 45
            reasons.append("direct match to the selected capability")
        elif supporting_cap_hit:
            score += 25
            reasons.append("related capability fit")

        if industry_hit:
            score += 25
            reasons.append(f"relevant to {industry_q}")

        if audience_hit:
            score += 15
            reasons.append("fits the target learner profile")

        if outcome_hit:
            score += 8
            reasons.append("supports the selected business outcome")

        if mode_hit:
            score += 3
            reasons.append("matches the preferred learning format")

        if duration_hit:
            score += 4
            reasons.append("fits the preferred duration")

        # Light free-text bonus only after the hard relevance gate.
        if challenge_q:
            challenge_words = {w for w in re.findall(r"[a-zA-Z]{5,}", _clean(challenge_q))}
            programme_text = " ".join([
                _text(row, ["Program Name", "Program Category", "Target Audience", "Capability Tags", "Business Outcome Tags"])
            ])
            overlap = [w for w in challenge_words if w in programme_text]
            if overlap:
                score += min(5, len(overlap))
                reasons.append("aligns with the described business challenge")

        # Small bonus when the curated capability tags also agree with primary domain.
        if primary_cap_hit and supporting_cap_hit:
            score += 3

        out = row.to_dict()
        out["_score"] = round(min(score, 100), 1)
        out["_rationale"] = "; ".join(dict.fromkeys(reasons)).capitalize() + "."
        out["_industry_match"] = industry_hit
        out["_capability_match"] = primary_cap_hit
        rows.append(out)

    if not rows:
        return pd.DataFrame(columns=list(data.columns) + ["_score", "_rationale", "_industry_match", "_capability_match"])

    result = pd.DataFrame(rows)

    # Keep only live/open programmes where a status field exists.
    for status_col in ["Status", "Program Status", "Programme Status", "Live Status"]:
        if status_col in result.columns:
            status = result[status_col].astype(str).str.lower().str.strip()
            live_mask = status.isin(["live", "active", "open", "yes", "currently live"])
            if live_mask.any():
                result = result[live_mask]
            break

    return (
        result.sort_values(["_score", "_industry_match"], ascending=[False, False])
              .head(top_n)
              .reset_index(drop=True)
    )
