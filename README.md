# Scholarix Trust Audit

**A prototype that catches when an AI's stated confidence contradicts its own reasoning.**

Built for the Scholarix AI two-week team evaluation task.

---

## The problem

Every record in `broad_impact.json` carries two AI-generated signals about the same claim:

- a `relevance_score` from 0–100 ("how confident am I this is genuinely about this researcher")
- a `reasoning` sentence explaining that score

These two signals should agree. Often they don't. A record can be scored **100/100** while its own `reasoning` says the content merely *"appears to be"* related, or is *"likely"* from the right source. That is the AI hedging in its own words while the number next to it claims certainty.

Across the provided dataset (50 researchers, 343 `broad_impact` records), **146 records (42.6%)** show this exact contradiction — a high stated score paired with hedging language in the AI's own explanation.

This matters because anyone using this data downstream — a research administrator, a hiring committee, a grant reviewer — is far more likely to glance at the number than to read the reasoning sentence closely. The number is what gets trusted, and in over 4 in 10 cases here, the number overstates what the AI itself actually believed.

## What this prototype does

1. Reads every `reasoning` string in every author's `broad_impact.json`.
2. Detects hedging language (`"appears to be"`, `"likely"`, `"possibly"`, `"unclear"`, ...) and definitive language (`"confirmed"`, `"verified"`, `"officially"`, ...).
3. Reconciles that language against the stated `relevance_score` and computes an **adjusted score**.
4. Assigns a plain-English verdict: **Consistent**, **Overstated Confidence**, or **Understated Confidence**.
5. Surfaces all of this in a dashboard: an aggregate audit across all 50 researchers, a "worst offenders" view, and a per-researcher drill-down where every flagged claim shows the original score struck through, the corrected score, and exactly which phrase triggered the correction.

Every flag is traceable to an exact phrase in the source text — this is a transparent, rule-based lexical audit, not a black-box model. See [Limitations](#limitations--known-issues) for what it does and doesn't catch.

## Why this direction (customer discovery link)

*(To be filled in with the specifics of your two interviews — see `docs/interview_question_rationale.md`.)* In short: research administrators and program staff who rely on this kind of aggregated researcher data said they don't have time to read every source explanation, but they do rely on scores/labels to triage what's trustworthy. A system that silently overstates confidence in 4 out of 10 records directly undermines that workflow — which is why we built a correction layer instead of, e.g., a duplicate-detector or a network graph.

---

## Project structure

```
scholarix-trust-audit/
├── README.md                       <- you are here
├── requirements.txt                 <- Python dependencies (Flask only)
├── backend/
│   ├── main.py                      <- Flask app: API routes + serves frontend
│   ├── data_loader.py               <- loads data/authors/* into memory
│   └── confidence_audit.py          <- the core audit algorithm (see docstring)
├── frontend/
│   ├── index.html                   <- dashboard shell
│   ├── styles.css                   <- "case file" design system
│   └── app.js                       <- fetches API, renders tables + evidence cards
├── data/
│   └── authors/<Name>/              <- the provided dataset (profile / publications / broad_impact)
└── tests/
    └── test_confidence_audit.py     <- unit + integration tests (stdlib unittest, no pytest needed)
```

## How to run it

**Requirements:** Python 3.10+. No paid APIs, no external services, no build step. Everything runs from one command.

```bash
# 1. From the project root, install the one dependency
pip install -r requirements.txt

# 2. Run the app (serves both the API and the frontend)
python -m backend.main

# 3. Open your browser to:
http://127.0.0.1:8000
```

That's it — the Flask app serves the dashboard at `/` and the JSON API at `/api/*` from the same process, so there's nothing else to configure or start.

### Running the tests

```bash
python -m unittest discover -s tests -v
```

12 tests covering: the core scoring logic on synthetic examples (including edge cases like missing data and score clamping), plus integration tests that run the full audit against the real provided dataset and check a known example stays flagged.

## API reference

| Endpoint | Description |
|---|---|
| `GET /api/health` | Confirms the server is up and how many authors loaded. |
| `GET /api/summary` | Aggregate audit stats across all 50 authors, plus the 8 most severe "worst offenders". |
| `GET /api/authors` | List of all authors with a per-author audit summary, sorted by most-flagged. |
| `GET /api/authors/<author_id>` | Full profile + every audited `broad_impact` record for one author. `author_id` is the folder name, e.g. `Andrew_A._Gewirth`. |

All responses are JSON. No authentication (local prototype, no sensitive/paid data involved).

## Data / source usage

- **Input data:** only the provided `data/authors/*` files (`profile.json`, `publications.json`, `broad_impact.json`). No external API calls are made by this prototype — the audit is purely a re-analysis of the AI-generated fields already present in the provided data.
- **No paid tools or services were used**, per the task constraints.
- `publications.json` (citation cross-source data) and `profile.json` (ORCID/affiliation data) are loaded and exposed via the API for context, but the current prototype's *audit logic* focuses specifically on `broad_impact.json`, per the chosen product direction — see [Scope](#scope) below.

## Scope

This prototype deliberately does **one thing well** rather than covering every data-quality issue found in the dataset. The team also identified (and documented separately in the data validation report):

- ~90% of publications show citation-count disagreement between OpenAlex and Crossref
- 18/50 authors have ORCID records listing multiple simultaneous "current institutions" (identity ambiguity)
- Every author's website/LinkedIn/Google Scholar verification fields are null or rate-limited (silent verification failure)

These are real, documented findings but are **out of scope for this prototype's UI** — building a system for all of them would produce the "broad, unfocused mega-dashboard" the task explicitly asks teams to avoid. They're listed here, and in the data validation report, as evidence the team explored the full dataset before choosing this direction.

## Limitations & known issues

- **Lexical, not semantic.** The audit matches known hedge/definitive phrases as substrings. It will miss uncertainty expressed in phrasing not in its phrase list, and (rarely) could match a phrase used in an unrelated sense. The phrase lists (`HEDGE_PHRASES` / `DEFINITIVE_PHRASES` in `confidence_audit.py`) are designed to be easy to extend.
- **No ground truth.** This tool flags *internal contradictions* (score vs. own reasoning), not whether the underlying relevance judgment is factually correct — we have no independent source to verify that against.
- **`Understated Confidence` is untriggered on this dataset** (0 of 343 records) — the AI in this dataset never uses definitive language on a low-scored record. The logic path is implemented and unit-tested, but real examples don't currently exist in the provided data; a synthetic test (`test_low_score_with_definitive_language_is_understated`) covers it.
- **Not a production system.** No auth, no persistence/database (data is re-read into memory from JSON files at startup), no rate limiting. This is intentional for a focused prototype per the task's scope guidance.
- **Development server.** `python -m backend.main` runs Flask's built-in dev server, which is fine for a local demo/evaluation but is not meant for production traffic (Flask prints this warning itself on startup).

## AI/tool usage note

This prototype (backend logic, frontend, tests, and this README) was developed with AI assistance (Claude). Specifically:
- The core hedge/definitive phrase lists were AI-drafted from patterns observed in the actual `broad_impact.json` reasoning text, then spot-checked by hand against real records.
- All aggregate statistics quoted in this README (146/343 overstated, etc.) were generated by running the actual code in this repository against the actual provided dataset — not estimated or invented.
- A bug in the phrase-matching logic (a negation, e.g. "could **not be confirmed**", was initially being counted as a *definitive* signal because it contains the word "confirmed") was caught by the test suite and fixed — see `_find_phrases` in `confidence_audit.py` for the mask-based fix.
- *(Team: add here what else AI was used for — e.g. interview question drafting, data exploration scripts — and how each output was checked before being relied on.)*

---

## Next steps (what we'd build next)

- Extend the same confidence-reconciliation logic to `publications.json`'s `deep_verification` fields (Semantic Scholar match confidence vs. citation-count agreement across sources).
- Replace the static phrase-weight lists with a small, explainable classifier trained on labeled examples, while keeping the "show the exact phrase that triggered this" transparency.
- Add an admin "accept correction" action so a human reviewer can confirm or override an adjusted score, turning this from a read-only audit into a review workflow.
