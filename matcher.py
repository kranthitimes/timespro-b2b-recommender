import re
import pandas as pd


# -----------------------------------------------------------------------------
# Normalisation dictionaries
# -----------------------------------------------------------------------------
INDUSTRY_ALIASES = {
    "banking & financial services": [
        "bfsi", "banking", "financial services", "finance", "fintech", "nbfc",
        "insurance", "capital markets", "investment banking", "wealth management"
    ],
    "technology / it & ites": [
        "technology", "it", "ites", "software", "digital", "saas", "tech"
    ],
    "manufacturing": [
        "manufacturing", "industrial", "operations", "factory", "production"
    ],
    "consulting & professional services": [
        "consulting", "professional services", "advisory"
    ],
    "retail & e-commerce": [
        "retail", "e-commerce", "ecommerce", "consumer", "digital commerce"
    ],
    "healthcare & pharma": [
        "healthcare", "pharma", "pharmaceutical", "hospital", "life sciences"
    ],
    "energy & infrastructure": [
        "energy", "infrastructure", "power", "oil", "gas", "utilities"
    ],
    "fmcg": [
        "fmcg", "consumer goods", "consumer products"
    ],
    "automotive": [
        "automotive", "automobile", "mobility", "ev", "electric vehicle"
    ],
    "telecom": [
        "telecom", "telecommunications"
    ],
    "government / psu": [
        "government", "psu", "public sector", "public administration"
    ],
}

CAPABILITY_ALIASES = {
    "finance & banking": [
        "finance", "banking", "fintech", "financial", "cfo", "capital markets",
        "investment banking", "credit", "risk", "wealth", "treasury", "valuation",
        "corporate finance", "financial management"
    ],
    "leadership & general management": [
        "leadership", "general management", "management", "executive leadership",
        "business leadership", "strategic leadership", "people leadership"
    ],
    "artificial intelligence & genai": [
        "artificial intelligence", "ai", "genai", "generative ai", "machine learning",
        "agentic ai", "ai for business"
    ],
    "data & analytics": [
        "data", "analytics", "business analytics", "data science", "bi", "statistics"
    ],
    "digital transformation": [
        "digital transformation", "digital strategy", "transformation", "digital business"
    ],
    "sales & marketing": [
        "sales", "marketing", "brand", "digital marketing", "customer experience",
        "consumer behaviour"
    ],
    "operations & supply chain": [
        "operations", "supply chain", "logistics", "procurement", "operations management"
    ],
    "project / product management": [
        "project management", "product management", "product leadership", "program management",
        "programme management", "agile"
    ],
    "hr & people leadership": [
        "hr", "human resources", "people management", "talent management", "chro",
        "people leadership"
    ],
    "strategy & business transformation": [
        "strategy", "strategic management", "business transformation", "corporate strategy",
        "geopolitics", "business strategy"
    ],
    "cybersecurity / cloud / technology": [
        "cybersecurity", "cyber security", "cloud", "technology", "software", "it",
        "digital technology"
    ],
    "sustainability / esg": [
        "sustainability", "esg", "climate", "environment", "green"
    ],
    "public policy": [
        "public policy", "policy", "governance", "public administration"
    ],
}

SENIORITY_ALIASES = {
    "early career / individual contributors": [
        "early career", "individual contributor", "young professional", "0-3 years",
        "0–3 years", "entry level"
    ],
    "first-time managers": [
        "first-time manager", "new manager", "team lead", "people manager"
    ],
    "mid-level managers": [
        "mid-level", "mid level", "middle management", "manager", "5+ years", "6+ years",
        "7+ years", "8+ years"
    ],
    "senior leaders": [
        "senior leader", "senior management", "leadership", "10+ years", "12+ years",
        "15+ years", "business head", "functional head"
    ],
    "functional specialists": [
        "specialist", "functional", "domain expert", "professional"
    ],
    "cxo / business leaders": [
        "cxo", "cxos", "chief", "ceo", "cfo", "chro", "cto", "cio", "business leader",
        "senior executive", "executive leadership"
    ],
}

BUSINESS_OUTCOME_ALIASES = {
    "build leadership pipeline": [
        "leadership", "leadership pipeline", "future leaders", "managerial capability"
    ],
    "upskill existing workforce": [
        "upskill", "capability building", "skill development", "professional development"
    ],
    "reskill for new roles": [
        "reskill", "career transition", "new roles", "role transition"
    ],
    "drive ai / digital adoption": [
        "ai adoption", "digital adoption", "digital transformation", "genai", "ai"
    ],
    "improve functional capability": [
        "functional capability", "domain capability", "functional expertise"
    ],
    "prepare high-potential talent": [
        "high potential", "hipo", "future leader", "leadership development"
    ],
    "support succession planning": [
        "succession", "leadership pipeline", "future leadership"
    ],
    "improve productivity / execution": [
        "productivity", "execution", "operational excellence", "performance"
    ],
    "create cross-functional business leaders": [
        "cross-functional", "general management", "business leadership", "enterprise leadership"
    ],
}


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def _flatten_aliases(value, alias_map):
    """Return canonical label + useful synonyms for matching."""
    if not value:
        return []
    key = _clean(value)
    vals = [key]
    vals.extend(alias_map.get(key, []))
    return list(dict.fromkeys([_clean(v) for v in vals if _clean(v)]))


def _flatten_multi_aliases(values, alias_map):
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    out = []
    for value in values:
        out.extend(_flatten_aliases(value, alias_map))
    return list(dict.fromkeys(out))


def _normalise_text(text):
    text = _clean(text)
    text = re.sub(r"[^a-z0-9+&/\- ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _phrase_hit(text, phrases):
    """Phrase-first matching with a conservative token fallback."""
    text = _normalise_text(text)
    if not text:
        return False, []

    hits = []
    for phrase in phrases:
        phrase = _normalise_text(phrase)
        if not phrase:
            continue
        if phrase in text:
            hits.append(phrase)
            continue

        # fallback: only meaningful words, to avoid tiny token false positives
        words = [w for w in phrase.split() if len(w) >= 4]
        if words and all(w in text for w in words):
            hits.append(phrase)

    return bool(hits), list(dict.fromkeys(hits))


def _combine(row, cols):
    parts = []
    for c in cols:
        if c in row.index and pd.notna(row[c]):
            parts.append(str(row[c]))
    return " | ".join(parts)


def _duration_match(duration_text, requested):
    if not requested or requested == "No preference":
        return False

    text = _clean(duration_text)
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if not nums:
        return False

    try:
        months = float(nums[0])
    except ValueError:
        return False

    if "< 3" in requested:
        return months < 3
    if "3–6" in requested or "3-6" in requested:
        return 3 <= months <= 6
    if "6–9" in requested or "6-9" in requested:
        return 6 <= months <= 9
    if "9–12" in requested or "9-12" in requested:
        return 9 <= months <= 12
    if "12+" in requested:
        return months >= 12
    return False


def _free_text_overlap(challenge_text, programme_text):
    challenge_words = {
        w for w in re.findall(r"[a-zA-Z]{4,}", _clean(challenge_text))
        if w not in {"with", "that", "this", "from", "into", "have", "need", "want", "their", "about"}
    }
    programme_words = set(re.findall(r"[a-zA-Z]{4,}", _clean(programme_text)))
    return challenge_words & programme_words


# -----------------------------------------------------------------------------
# Main recommendation engine
# -----------------------------------------------------------------------------
def recommend_programs(df, requirements, top_n=8):
    """
    Hierarchical B2B recommendation engine.

    Weighting:
      - Capability relevance: 35
      - Industry relevance: 30
      - Seniority fit: 15
      - Business outcome fit: 10
      - Delivery mode: 5
      - Duration: 5
      - Free-text challenge: up to +5 bonus

    Gating rule:
      A programme must match either the selected industry OR selected capability.
      If capability is explicitly selected, capability matches are preferred strongly.
    """

    data = df.copy()

    aliases = {
        "industry": [
            "Industry", "Industries", "Industry Tags", "Relevant Industries",
            "Industry Relevance"
        ],
        "audience": [
            "Target Audience", "Ideal Candidate Profile", "Audience", "Seniority",
            "Seniority Tags", "Work Experience", "Eligibility"
        ],
        "capability": [
            "Program Category", "Programme Category", "Category", "Capability", "Domain",
            "Skills", "Keywords", "Capability Tags", "Function Tags", "Role / Function Tags"
        ],
        "goal": [
            "Business Outcome", "Business Outcome Tags", "Use Cases", "Learning Outcomes",
            "Program Overview", "Programme Overview", "Description"
        ],
        "mode": ["Mode", "Delivery Mode", "Learning Format"],
        "duration": ["Duration (Months)", "Duration", "Duration (in months)"],
        "description": [
            "Program Name", "Programme Name", "Institute", "Program Overview", "Programme Overview",
            "Description", "Curriculum", "Keywords", "Target Audience"
        ],
    }

    industry_q = requirements.get("industry", "")
    audience_q = requirements.get("audience", [])
    capability_q = requirements.get("capability", [])
    goal_q = requirements.get("business_goal", [])
    mode_q = requirements.get("mode", [])
    duration_q = requirements.get("duration", "")
    challenge_q = requirements.get("challenge", "")

    industry_terms = _flatten_aliases(industry_q, INDUSTRY_ALIASES)
    audience_terms = _flatten_multi_aliases(audience_q, SENIORITY_ALIASES)
    capability_terms = _flatten_multi_aliases(capability_q, CAPABILITY_ALIASES)
    goal_terms = _flatten_multi_aliases(goal_q, BUSINESS_OUTCOME_ALIASES)
    mode_terms = [_clean(x) for x in mode_q] if mode_q else []

    scores = []
    rationales = []
    gate_flags = []
    capability_flags = []
    industry_flags = []

    for _, row in data.iterrows():
        score = 0.0
        reasons = []

        industry_text = _combine(row, aliases["industry"] + aliases["description"])
        audience_text = _combine(row, aliases["audience"] + aliases["description"])
        capability_text = _combine(row, aliases["capability"] + aliases["description"])
        goal_text = _combine(row, aliases["goal"] + aliases["description"])
        mode_text = _combine(row, aliases["mode"])
        duration_text = _combine(row, aliases["duration"])
        all_text = " | ".join([
            industry_text, audience_text, capability_text,
            goal_text, mode_text, duration_text
        ])

        # 1) Capability fit - highest weight
        capability_hit, capability_hits = _phrase_hit(capability_text, capability_terms)
        if capability_hit:
            score += 35
            reasons.append("strong capability match")

        # 2) Industry fit
        industry_hit, industry_hits = _phrase_hit(industry_text, industry_terms)
        if industry_hit:
            score += 30
            reasons.append(f"relevant to {industry_q}")

        # 3) Seniority / learner profile
        audience_hit, audience_hits = _phrase_hit(audience_text, audience_terms)
        if audience_hit:
            score += 15
            reasons.append("fits the target learner seniority")

        # 4) Business outcome
        goal_hit, goal_hits = _phrase_hit(goal_text, goal_terms)
        if goal_hit:
            score += 10
            reasons.append("supports the selected business outcome")

        # 5) Delivery mode
        mode_hit, mode_hits = _phrase_hit(mode_text, mode_terms)
        if mode_hit:
            score += 5
            reasons.append("matches the preferred learning format")

        # 6) Duration
        if _duration_match(duration_text, duration_q):
            score += 5
            reasons.append("fits the preferred duration")

        # Small free-text bonus only; never enough to overcome poor core fit
        overlap = _free_text_overlap(challenge_q, all_text)
        if overlap:
            score += min(5, len(overlap))
            reasons.append("aligns with the described business challenge")

        # Strong relevance gate: must match industry OR capability.
        gate = industry_hit or capability_hit

        # If a specific capability is selected, avoid non-capability matches dominating
        # purely due to seniority. Industry-only matches are retained but score lower.
        if capability_q and industry_hit and not capability_hit:
            score *= 0.55

        # If capability matches but industry doesn't, keep it because some programmes
        # are industry-agnostic (e.g. Finance/CFO or Leadership programmes).
        if capability_hit and not industry_hit:
            score *= 0.90

        scores.append(round(min(score, 100), 1))
        rationales.append(
            "; ".join(dict.fromkeys(reasons)).capitalize() + "."
            if reasons else "No strong fit on the selected B2B criteria."
        )
        gate_flags.append(gate)
        capability_flags.append(capability_hit)
        industry_flags.append(industry_hit)

    data["_score"] = scores
    data["_rationale"] = rationales
    data["_gate"] = gate_flags
    data["_capability_match"] = capability_flags
    data["_industry_match"] = industry_flags

    # Keep only active/live programmes where such a status column exists.
    for status_col in ["Status", "Program Status", "Programme Status", "Live Status"]:
        if status_col in data.columns:
            status = data[status_col].astype(str).str.lower().str.strip()
            live_mask = status.isin(["live", "active", "open", "yes", "currently live"])
            if live_mask.any():
                data = data[live_mask]
            break

    # Core relevance gate removes irrelevant recommendations such as healthcare
    # for a BFSI + Finance requirement.
    data = data[data["_gate"]]

    # Prefer capability matches first when the user selected a capability,
    # then sort by final score and industry fit.
    sort_cols = []
    ascending = []
    if capability_q:
        sort_cols.append("_capability_match")
        ascending.append(False)
    sort_cols.extend(["_score", "_industry_match"])
    ascending.extend([False, False])

    return (
        data.sort_values(sort_cols, ascending=ascending)
            .head(top_n)
            .reset_index(drop=True)
    )
