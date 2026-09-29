import re
import pandas as pd

MATCHER_VERSION = "4.0"

INDUSTRY_ALIASES = {
    "banking & financial services": ["bfsi", "banking", "financial services", "fintech", "nbfc", "insurance", "capital markets", "investment banking", "wealth management", "asset management"],
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

# These terms are intentionally strict and are checked only against Program Name + Program Category.
PRIMARY_DOMAIN_TERMS = {
    "finance & banking": [
        "finance", "financial", "banking", "fintech", "cfo", "capital market", "investment banking",
        "credit", "wealth", "treasury", "valuation", "quantitative finance", "risk management"
    ],
    "leadership & general management": [
        "leadership", "general management", "executive management", "business leadership",
        "management development", "cxO leadership".lower()
    ],
    "artificial intelligence & genai": [
        "artificial intelligence", "generative ai", "gen ai", "genai", "agentic ai", "ai for business", "ai for leaders"
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

# Specialized domains that should not be mistaken for broad Leadership/General Management.
LEADERSHIP_EXCLUSIONS = [
    "healthcare management", "project management", "product management", "supply chain", "fintech",
    "finance", "banking", "marketing", "sales", "data science", "analytics", "cybersecurity",
    "public policy", "sustainability", "esg"
]

SENIORITY_ALIASES = {
    "early career / individual contributors": ["early career", "individual contributor", "young professional", "entry level", "0-3 years", "0–3 years"],
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
    for term in terms or []:
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
    primary_text = _text(row, ["Program Name", "Programme Name", "Program Category", "Programme Category", "Category"])
    matched = []
    for cap in selected_capabilities or []:
        key = _clean(cap)
        terms = PRIMARY_DOMAIN_TERMS.get(key, [key])
        hit, _ = _has(primary_text, terms)
        if not hit:
            continue
        # Broad leadership should not be inferred from specialized management programmes.
        if key == "leadership & general management":
            exclusion_hit, _ = _has(primary_text, LEADERSHIP_EXCLUSIONS)
            explicit_leadership_hit, _ = _has(primary_text, ["leadership", "general management", "executive management", "business leadership", "management development", "cxo leadership"])
            if exclusion_hit and not explicit_leadership_hit:
                continue
        matched.append(cap)
    return bool(matched), matched


def _industry_match(row, selected_industry):
    if not selected_industry or _clean(selected_industry) == "other":
        return True, False
    tags = _text(row, ["Industry Tags", "Industry", "Relevant Industries"])
    terms = _expanded(selected_industry, INDUSTRY_ALIASES)
    direct, _ = _has(tags, terms)
    universal, _ = _has(tags, ["cross-industry", "cross industry", "all industries", "industry agnostic"])
    return direct or universal, direct


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
    """TimesPro B2B recommendation engine v4.0.

    Rules:
    1) If capability is selected, programme name/category must genuinely match that capability.
    2) If industry is selected, programme must be either explicitly relevant to that industry or tagged Cross-industry.
    3) Broad auto-generated Capability Tags never qualify a programme by themselves.
    4) Audience/outcome/mode/duration only rank programmes after relevance gates are passed.
    """
    data = df.copy()

    industry_q = requirements.get("industry", "")
    capabilities_q = requirements.get("capability", []) or []
    audience_q = requirements.get("audience", []) or []
    outcomes_q = requirements.get("business_goal", []) or []
    modes_q = requirements.get("mode", []) or []
    duration_q = requirements.get("duration", "")
    challenge_q = requirements.get("challenge", "")

    audience_terms = _expanded(audience_q, SENIORITY_ALIASES)
    outcome_terms = _expanded(outcomes_q, BUSINESS_OUTCOME_ALIASES)
    mode_terms = [_clean(x) for x in modes_q]

    rows = []
    for _, row in data.iterrows():
        primary_cap_hit, primary_cap_labels = _primary_capability_match(row, capabilities_q)
        industry_allowed, direct_industry_hit = _industry_match(row, industry_q)

        # Mandatory relevance gates
        if capabilities_q and not primary_cap_hit:
            continue
        if industry_q and _clean(industry_q) != "other" and not industry_allowed:
            continue

        audience_text = _text(row, ["Seniority Tags", "Target Audience", "Work Experience", "Eligibility"])
        outcome_text = _text(row, ["Business Outcome Tags", "Target Audience", "Program Name", "Program Category"])
        mode_text = _text(row, ["Mode", "Delivery Mode", "Learning Format"])
        duration_text = _text(row, ["Duration (Months)", "Duration", "Duration (in months)"])

        audience_hit, _ = _has(audience_text, audience_terms)
        outcome_hit, _ = _has(outcome_text, outcome_terms)
        mode_hit, _ = _has(mode_text, mode_terms)
        duration_hit = _duration_match(duration_text, duration_q)

        score = 0.0
        reasons = []

        if primary_cap_hit:
            score += 50
            reasons.append("direct match to the selected capability")

        if direct_industry_hit:
            score += 25
            reasons.append(f"directly relevant to {industry_q}")
        elif industry_allowed and industry_q:
            score += 12
            reasons.append("applicable across industries")

        if audience_hit:
            score += 15
            reasons.append("fits the target learner profile")

        if outcome_hit:
            score += 6
            reasons.append("supports the selected business outcome")

        if mode_hit:
            score += 2
            reasons.append("matches the preferred learning format")

        if duration_hit:
            score += 2
            reasons.append("fits the preferred duration")

        # Free-text challenge only acts as a small tie-breaker.
        challenge_words = {w for w in re.findall(r"[a-zA-Z]{5,}", _clean(challenge_q))}
        primary_text = _text(row, ["Program Name", "Program Category", "Target Audience"])
        programme_words = {w for w in re.findall(r"[a-zA-Z]{5,}", primary_text)}
        overlap = challenge_words & programme_words
        if overlap:
            score += min(3, len(overlap))
            reasons.append("aligns with the stated challenge")

        score = min(round(score), 100)
        item = row.copy()
        item["_score"] = score
        item["_rationale"] = "; ".join(reasons).capitalize() + "."
        item["_matched_capabilities"] = ", ".join(primary_cap_labels)
        rows.append(item)

    if not rows:
        return pd.DataFrame(columns=list(data.columns) + ["_score", "_rationale", "_matched_capabilities"])

    result = pd.DataFrame(rows)

    for status_col in ["Status", "Program Status", "Live Status"]:
        if status_col in result.columns:
            live_mask = result[status_col].astype(str).str.strip().str.lower().isin(["live", "active", "open", "yes"])
            if live_mask.any():
                result = result[live_mask]
            break

    return result.sort_values(["_score", "Program Name"], ascending=[False, True]).head(top_n).reset_index(drop=True)
