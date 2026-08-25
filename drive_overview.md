# Scholarix Trust Audit — Submission Overview

**Team folder:** `Team_AmanJoshi_AnanyaGupta`

## Team

| Role | Name | Email |
|---|---|---|
| Product & Research Operations | Ananya Gupta | ananya21@illinois.edu |
| Full Stack Developer | Aman Joshi | abj4@illinois.edu |

## Code repository

**GitHub:** https://github.com/AmanJoshi2004/scholarix-trust-audit

The repository is public and contains all source code, tests, data, and documentation. See the README in the repo for setup and run instructions (`pip install -r requirements.txt` then `python -m backend.main`, open `http://127.0.0.1:8000`).

## One-paragraph summary

Scholarix AI's `broad_impact.json` records carry an AI-generated relevance score alongside a text explanation of that score — and in 42.6% of the 343 records we audited across all 50 provided researchers, the two contradict each other: a near-certain score (90–100) paired with reasoning that hedges ("appears to be," "likely"). We built a working prototype that detects this contradiction, computes a corrected confidence score, and shows the user the original score, the corrected score, and the exact phrase that triggered the correction — always together, never a silent replacement. This direction was directly validated by two customer interviews, both of which independently confirmed the core hypothesis and specifically requested that any correction come with visible evidence rather than an unexplained new number.

## Where to find each deliverable in this Drive folder

| Deliverable | File |
|---|---|
| Product brief | `product_brief.md` (or .pdf/.docx if converted) |
| Customer interview report | `customer_interview_report.md` |
| Interview question rationale | `interview_question_rationale.md` |
| Data validation report | `data_validation_report.md` |
| Pitch deck | `scholarix_trust_audit_pitch.pptx` |
| AI/tool usage note | `ai_usage_note.md` |
| Demo screenshots / recording | [add — see note below] |
| GitHub repo link | this document, and also in the pitch deck's closing slide |

## Still needed before submission

- [ ] Add full stack developer's real name + both emails above
- [ ] Add a short demo recording or a few more screenshots of the running prototype (dashboard view, worst-offenders view, one researcher drill-down) to this Drive folder
- [ ] Confirm GitHub repo access is open (public repo — already satisfied) or grant reviewer access if made private
- [ ] Double check all files are uploaded before Friday, August 28, 2026
