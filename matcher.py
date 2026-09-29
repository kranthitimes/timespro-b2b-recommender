
import re
import pandas as pd

def _clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()

def _tokens(values):
    if values is None:
        return set()
    if isinstance(values, str):
        values = [values]
    out = set()
    for v in values:
        text = _clean(v)
        for token in re.split(r"[,;/|&\n]+", text):
            token = token.strip()
            if token:
                out.add(token)
    return out

def _contains_any(text, values):
    text = _clean(text)
    if not text:
        return False, []
    hits = []
    for v in values:
        v = _clean(v)
        if v and (v in text or any(w in text for w in v.split() if len(w) > 3)):
            hits.append(v)
    return bool(hits), hits

def recommend_programs(df, requirements, top_n=8):
    """
    Weighted rule-based matcher.
    Replace or augment this with embeddings/LLM later if desired.
    """

    data = df.copy()

    aliases = {
        "industry": ["Industry", "Industries", "Industry Tags", "Relevant Industries"],
        "audience": ["Target Audience", "Ideal Candidate Profile", "Audience", "Seniority"],
        "capability": ["Program Category", "Category", "Capability", "Domain", "Skills", "Keywords"],
        "goal": ["Business Outcome", "Use Cases", "Learning Outcomes", "Program Overview", "Programme Overview"],
        "mode": ["Mode", "Delivery Mode", "Learning Format"],
        "duration": ["Duration", "Duration (in months)"],
        "description": ["Program Overview", "Programme Overview", "Description", "Curriculum", "Keywords"],
    }

    def combine(row, cols):
        parts = []
        for c in cols:
            if c in row.index and pd.notna(row[c]):
                parts.append(str(row[c]))
        return " | ".join(parts)

    industry_q = requirements.get("industry", "")
    audience_q = requirements.get("audience", [])
    capability_q = requirements.get("capability", [])
    goal_q = requirements.get("business_goal", [])
    mode_q = requirements.get("mode", [])
    duration_q = requirements.get("duration", "")
    challenge_q = requirements.get("challenge", "")

    scores = []
    rationales = []

    for _, row in data.iterrows():
        score = 0
        reasons = []

        industry_text = combine(row, aliases["industry"] + aliases["description"])
        audience_text = combine(row, aliases["audience"] + aliases["description"])
        capability_text = combine(row, aliases["capability"] + aliases["description"])
        goal_text = combine(row, aliases["goal"] + aliases["description"])
        mode_text = combine(row, aliases["mode"])
        duration_text = combine(row, aliases["duration"])
        all_text = " | ".join([industry_text, audience_text, capability_text, goal_text, mode_text, duration_text])

        ok, _ = _contains_any(industry_text, [industry_q])
        if ok:
            score += 22
            reasons.append(f"relevant to {industry_q}")

        ok, _ = _contains_any(audience_text, audience_q)
        if ok:
            score += 18
            reasons.append("fits the target learner profile")

        ok, hits = _contains_any(capability_text, capability_q)
        if ok:
            score += min(30, 15 + 7 * len(hits))
            reasons.append("matches priority capability areas")

        ok, hits = _contains_any(goal_text, goal_q)
        if ok:
            score += min(18, 10 + 4 * len(hits))
            reasons.append("supports the stated business outcomes")

        ok, _ = _contains_any(mode_text, mode_q)
        if ok:
            score += 7
            reasons.append("matches preferred delivery format")

        if duration_q and duration_q != "No preference":
            ok, _ = _contains_any(duration_text, [duration_q])
            if ok:
                score += 5

        # Free-text challenge gets a light keyword-overlap score.
        challenge_words = {w for w in re.findall(r"[a-zA-Z]{4,}", _clean(challenge_q))}
        programme_words = {w for w in re.findall(r"[a-zA-Z]{4,}", _clean(all_text))}
        overlap = challenge_words & programme_words
        if overlap:
            score += min(10, len(overlap) * 2)
            reasons.append("aligns with the described capability challenge")

        score = min(score, 100)
        scores.append(score)
        rationales.append("; ".join(dict.fromkeys(reasons)).capitalize() + "." if reasons else "General catalogue match.")

    data["_score"] = scores
    data["_rationale"] = rationales

    # Optional active/live filter
    for status_col in ["Status", "Program Status", "Live Status"]:
        if status_col in data.columns:
            live_mask = data[status_col].astype(str).str.lower().isin(["live", "active", "open", "yes"])
            if live_mask.any():
                data = data[live_mask]
            break

    return (
        data.sort_values(["_score"], ascending=False)
            .head(top_n)
            .reset_index(drop=True)
    )
