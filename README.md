
# TimesPro B2B Programme Recommender

A Streamlit prototype for helping TimesPro B2B teams identify relevant executive education programmes for enterprise L&D requirements.

## What the app does

1. Captures enterprise context:
   - Industry
   - Target learner group
   - Learner population
   - Priority capability areas
   - Desired business outcomes
   - Learning format
   - Duration
   - Free-text capability challenge

2. Reads a TimesPro programme master from:
   `data/program_master.xlsx`

3. Scores programmes using a transparent weighted matching engine.

4. Presents a shortlist with:
   - Programme / institute
   - Category
   - Duration
   - Mode
   - Fee
   - Match score
   - "Why it fits" rationale
   - Programme link

5. Lets the user download the shortlist.

---

## Recommended Excel columns

The matcher tolerates different names, but the ideal master is:

- Program Name
- Institute Name
- Program Category
- Program Overview
- Target Audience
- Industry Tags
- Business Outcome
- Skills
- Duration
- Fee
- Mode
- Immersion
- Eligibility
- Work Experience
- Program Link
- Status

### Important: add tagging columns

For strong B2B recommendations, do not rely only on programme descriptions. Add:

- Industry Tags
- Role / Function Tags
- Seniority Tags
- Capability Tags
- Business Outcome Tags
- Delivery Tags

Example:

Industry Tags:
`BFSI; Consulting; FinTech`

Capability Tags:
`AI; GenAI; Digital Transformation; Leadership`

Business Outcome Tags:
`AI adoption; productivity; transformation leadership`

---

## Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## GitHub + Streamlit Community Cloud

1. Create a GitHub repository.
2. Add:
   - `app.py`
   - `matcher.py`
   - `requirements.txt`
   - `data/program_master.xlsx`
3. Push the repository.
4. In Streamlit Community Cloud, create a new app.
5. Select the GitHub repository and `app.py`.
6. Deploy.

For a client-facing production deployment, use a private/controlled data source instead of keeping sensitive programme or pricing data in a public GitHub repository.

---

## Suggested next version

### Phase 1 — Internal MVP
Rule-based matching, Excel master, shortlist export.

### Phase 2 — Smarter matching
Add:
- taxonomy/synonym tables
- role-to-skill maps
- industry-to-capability maps
- embeddings for semantic matching
- curated programme boost/suppress rules

### Phase 3 — Sales enablement
Generate:
- branded client recommendation page
- PDF proposal
- shareable unique link
- CRM lead record
- enquiry owner / SPOC
- analytics on top searched capabilities and recommended programmes

---

## Suggested architecture

Client browser
→ Streamlit discovery interface
→ Requirement normalisation
→ Industry / Role / Capability taxonomy
→ Recommendation engine
→ TimesPro programme master
→ Ranked shortlist
→ Export / share / CRM

The matching engine is deliberately separated into `matcher.py` so the UI can evolve without changing recommendation logic.
