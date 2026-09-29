import re
import pandas as pd

MATCHER_VERSION = "4.1"

INDUSTRY_ALIASES = {
    "banking & financial services": [
        "bfsi", "banking", "financial services", "finance", "fintech",
        "capital markets", "investment banking", "wealth", "insurance",
        "credit", "risk", "treasury"
    ],
    "technology / it & ites": [
        "technology", "it", "ites", "software", "digital", "cloud",
        "cyber", "cybersecurity", "data", "ai", "analytics"
    ],
    "manufacturing": ["manufacturing", "operations", "supply chain", "industrial", "quality"],
    "consulting & professional services": ["consulting", "professional services", "strategy", "transformation"],
    "retail & e-commerce": ["retail", "ecommerce", "e-commerce", "consumer", "digital commerce"],
    "healthcare & pharma": ["healthcare", "pharma", "hospital", "life sciences"],
    "energy & infrastructure": ["energy", "infrastructure", "power", "oil", "gas", "renewable"],
    "fmcg": ["fmcg", "consumer", "brand", "marketing", "sales"],
    "automotive": ["automotive", "manufacturing", "mobility"],
    "telecom": ["telecom", "technology", "digital"],
    "government / psu": ["government", "public policy", "public sector", "psu"]
}

CAPABILITY_ALIASES = {
    "finance & banking": [
        "finance", "financial", "banking", "fintech", "capital markets",
        "investment banking", "cfo", "credit", "risk", "treasury",
        "wealth", "valuation", "corporate finance"
    ],
    "leadership & general management": [
        "leadership", "general management", "business management",
        "strategic management", "executive leadership", "cxO leadership",
        "management development"
    ],
    "artificial intelligence & genai": [
        "artificial intelligence", " ai ", "genai", "generative ai",
        "machine learning", "agentic ai"
    ],
    "data & analytics": [
        "data science", "data analytics", "analytics", "business analytics",
        "machine learning"
    ],
    "digital transformation": [
        "digital transformation", "digital strategy", "technology transformation"
    ],
    "sales & marketing": [
        "sales", "marketing", "brand", "digital marketing", "customer experience"
    ],
    "operations & supply chain": [
        "operations", "supply chain", "logistics", "procurement"
    ],
    "project / product management": [
        "project management", "product management", "programme management",
        "program management"
    ],
    "hr & people leadership": [
        "human resources", "hr", "people management", "talent management",
        "chro", "people leadership"
    ],
    "strategy & business transformation": [
        "strategy", "business transformation", "strategic leadership",
        "corporate strategy", "transformation"
    ],
    "cybersecurity / cloud / technology": [
        "cybersecurity", "cyber security", "cloud", "technology", "software"
    ],
    "sustainability / esg": [
        "sustainability", "esg", "climate", "environment"
    ],
    "public policy": ["public policy", "policy", "governance"]
}

AUDIENCE_ALIASES = {
    "early career / individual contributors": ["early career", "individual contributor", "young professional"],
    "first-time managers": ["first-time manager", "new manager", "junior manager"],
    "mid-level managers": ["mid-level", "middle management", "manager", "5 years", "7 years", "8 years"],
    "senior leaders": ["senior leader", "senior management", "leadership", "10 years", "12 years", "15 years"],
    "functional specialists": ["specialist", "functional professional", "domain expert"],
    "cxo / business leaders": ["cxo", "ceo", "cfo", "chro", "business leader", "executive leader"]
}

def _clean(v):
    if pd.isna(v):
        return ""
    return re.sub(r"\s+", " ", str(v).strip().lower())

def _row_text(row, cols):
    parts = []
    for c in cols:
        if c in row.index and pd.notna(row[c]):
            parts.append(str(row[c]))
    return _clean(" | ".join(parts))

def _aliases(selected, mapping):
    out = []
    for item in selected if isinstance(selected, list) else [selected]:
        key = _clean(item)
        out.append(key)
        out.extend(mapping.get(key, []))
    return [x for x in dict.fromkeys(_clean(x) for x in out) if x]

def _has_any(text, terms):
    hits = []
    for term in terms:
        t = _clean(term)
        if not t:
            continue
        # special handling for standalone AI
        if t == "ai":
            if re.search(r"\bai\b", text):
                hits.append(t)
        elif t in text:
            hits.append(t)
    return bool(hits), hits

def _duration_match(duration_text, requested):
    if not requested or requested == "No preference":
        return True
    nums = re.findall(r"\d+(?:\.\d+)?", duration_text)
    if not nums:
        return False
    try:
        months = float(nums[0])
    except Exception:
        return False

    if requested == "< 3 months":
        return months < 3
    if requested == "3–6 months":
        return 3 <= months <= 6
    if requested == "6–9 months":
        return 6 <= months <= 9
    if requested == "9–12 months":
        return 9 <= months <= 12
    if requested == "12+ months":
        return months >= 12
    return False

def recommend_programs(df, requirements, top_n=8):
    data = df.copy()

    industry_q = requirements.get("industry", "")
    audience_q = requirements.get("audience", []) or []
    capability_q = requirements.get("capability", []) or []
    goal_q = requirements.get("business_goal", []) or []
    mode_q = requirements.get("mode", []) or []
    duration_q = requirements.get("duration", "No preference")
    challenge_q = _clean(requirements.get("challenge", ""))

    industry_terms = _aliases(industry_q, INDUSTRY_ALIASES)
    capability_terms = _aliases(capability_q, CAPABILITY_ALIASES)
    audience_terms = _aliases(audience_q, AUDIENCE_ALIASES)

    results = []

    for idx, row in data.iterrows():
        name = _row_text(row, ["Program Name", "Programme Name"])
        category = _row_text(row, ["Program Category", "Programme Category", "Category"])
        overview = _row_text(row, ["Program Overview", "Programme Overview", "Description"])
        industry_text = _row_text(row, ["Industry Tags", "Relevant Industries", "Industries"])
        audience_text = _row_text(row, ["Target Audience", "Ideal Candidate Profile", "Seniority Tags", "Work Experience", "Eligibility"])
        outcome_text = _row_text(row, ["Business Outcome Tags", "Business Outcome", "Learning Outcomes", "Program Overview", "Programme Overview"])
        mode_text = _row_text(row, ["Mode", "Delivery Mode", "Learning Format"])
        duration_text = _row_text(row, ["Duration", "Duration (Months)", "Duration (in months)"])

        # Primary capability classification should rely on programme identity,
        # not broad auto-generated tags.
        primary_capability_text = " | ".join([name, category])
        cap_hit, cap_hits = _has_any(primary_capability_text, capability_terms)

        # If capability is explicitly selected, require a real capability match.
        if capability_q and not cap_hit:
            continue

        industry_hit, industry_hits = _has_any(
            " | ".join([industry_text, name, category, overview]),
            industry_terms
        )

        # Industry is important, but not every programme master has reliable industry tags.
        # We do not hard-filter on industry if capability is already a strong match.
        audience_hit, _ = _has_any(audience_text, audience_terms)

        goal_hit, _ = _has_any(outcome_text, goal_q)

        mode_hit, _ = _has_any(mode_text, mode_q)

        duration_hit = _duration_match(duration_text, duration_q)

        score = 0
        reasons = []

        if cap_hit:
            score += 40
            reasons.append("strong match to the selected capability")

        if industry_hit:
            score += 25
            reasons.append(f"relevant to {industry_q}")

        if audience_hit:
            score += 15
            reasons.append("fits the target learner profile")

        if goal_hit:
            score += 10
            reasons.append("supports the stated business outcome")

        if mode_hit:
            score += 5
            reasons.append("matches the preferred learning format")

        if duration_hit:
            score += 5
            reasons.append("matches the preferred duration")

        # Light free-text signal, capped so it cannot override domain relevance.
        if challenge_q:
            challenge_words = set(re.findall(r"[a-z]{4,}", challenge_q))
            programme_words = set(re.findall(r"[a-z]{4,}", " ".join([name, category, overview])))
            overlap = challenge_words & programme_words
            if overlap:
                bonus = min(5, len(overlap))
                score = min(100, score + bonus)

        # Down-rank unrelated specialist categories for broad leadership searches.
        selected_caps = {_clean(x) for x in capability_q}
        if "leadership & general management" in selected_caps:
            unrelated_specialist = [
                "healthcare management", "project management", "product management",
                "supply chain", "fintech", "finance", "data science", "cybersecurity",
                "marketing", "public policy"
            ]
            if any(x in primary_capability_text for x in unrelated_specialist):
                continue

        rec = row.copy()
        rec["_score"] = int(min(score, 100))
        rec["_rationale"] = "; ".join(dict.fromkeys(reasons)).capitalize() + "." if reasons else "Relevant programme match."
        results.append(rec)

    if not results:
        return pd.DataFrame(columns=list(data.columns) + ["_score", "_rationale"])

    out = pd.DataFrame(results)

    # Prefer live/active rows when such a field exists.
    for col in ["Status", "Program Status", "Live Status"]:
        if col in out.columns:
            live = out[col].astype(str).str.lower().isin(["live", "active", "open", "yes"])
            if live.any():
                out = out[live]
            break

    return (
        out.sort_values("_score", ascending=False)
           .head(top_n)
           .reset_index(drop=True)
    )
