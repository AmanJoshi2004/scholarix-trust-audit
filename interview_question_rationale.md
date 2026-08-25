# Interview Question Rationale — Scholarix Trust Audit

For each question: what it was designed to test, what we actually learned from P1 (Aditya) and P2 (Daksh), and how it shaped the prototype.

---

### Q1 — "Walk me through the last time you looked someone up..."

**Why this question was chosen:** To open with real behavior rather than a hypothetical, and to confirm this persona actually performs researcher lookups often enough to have a real, describable workflow.

**What we learned:** Both P1 and P2 independently described the same pattern: start with Google Scholar, then cross-check against a university page and LinkedIn, specifically *because* they don't trust any single source to be current. Both explicitly said they compare at least two sources for anything that matters.

**How it affected the prototype:** Confirmed that our target user already practices manual source cross-checking — meaning a tool that automates and surfaces that reconciliation has a real, existing behavior to slot into, rather than needing to create a new habit from scratch.

---

### Q2 — "Has a piece of information about a researcher ever turned out to be wrong or outdated?"

**Why this question was chosen:** To test whether "bad data" is a felt, remembered problem rather than a hypothetical concern — a concrete story is stronger evidence than a hypothetical "yes."

**What we learned:** Both P1 and P2 gave the *same* concrete story independently: a researcher's Google Scholar / older search results still showed a previous university affiliation while their current university page and LinkedIn showed they'd moved. Both also separately noted citation counts differing across platforms.

**How it affected the prototype:** This is an independent, real-world confirmation of a pattern we'd already found directly in the data (citation disagreement across OpenAlex/Crossref in ~90% of publications, and ORCID records listing multiple simultaneous "current institutions" in 18/50 authors). The interviews turned a data observation into a validated user pain point — which is why the data validation report leads with these exact two issues.

---

### Q3 — "Do you trust the score, or do you check the reasoning behind it?"

**Why this question was chosen:** This is the core hypothesis test for the entire product direction — that users anchor on a number and skip the explanation behind it.

**What we learned:** Both confirmed the hypothesis, but with an important nuance neither had been asked about directly: it's conditional, not absolute. Both described a "two-speed" trust pattern — high scores are trusted by default when skimming quickly, but the moment a decision actually matters (contacting someone, using the info for real work), both said they want to understand *why* the score is what it is.

**How it affected the prototype:** This nuance directly shaped the UI. Rather than hiding the audit behind a click (for "skim mode") or forcing everyone through detailed reasoning (for "decision mode"), the dashboard shows both: a fast scannable summary (the ledger stats, the sortable researcher table with overstated %) for skimming, and a full evidence card with score + reasoning + explanation one click away for when it matters.

---

### Q4 — "Would a 100%-confident score paired with hedging language in the reasoning bother you?"

**Why this question was chosen:** The closest thing to a direct concept test without naming the product — testing whether the core contradiction we found in the data actually registers as a problem to a real user, or whether we're the only ones who'd notice it.

**What we learned:** Immediate, strong "yes" from both, with no need to explain further — both understood the contradiction instantly and both said it would make them question the score. Daksh, from a quantitative background, added a sharper framing: "100% confidence should be reserved for information with very strong evidence" — over-claimed certainty bothered him more than an honestly lower score would.

**How it affected the prototype:** This was the strongest validation signal in either interview — it confirmed the product's central premise is not just internally logical but something real users notice and care about unprompted. No design change resulted from this question directly; instead, it justified building the prototype at all.

---

### Q5 — "What would make you stop trusting a researcher-data tool entirely?"

**Why this question was chosen:** To find the actual trust threshold — how aggressively the tool needs to flag problems, and what "too broken to use" looks like from the user's side.

**What we learned:** Both independently named the same top failure mode, in almost the same words: **repeated identity mix-ups** — two researchers with similar names or research areas being conflated — was described as the single biggest trust-breaker by both P1 and P2, ranked above outdated affiliations or citation disagreements. P2 added a sharp practical point: once he stops trusting the tool, "the tool wouldn't really be saving me much time" — i.e. the entire value proposition collapses, not just accuracy.

**How it affected the prototype:** This didn't change the current prototype's scope (which focuses on `broad_impact.json` confidence/reasoning contradictions, not identity resolution), but it is the single clearest, most consistent finding across both interviews and is documented as the top priority in the "Next steps" section of the README — identity-collision detection (the ORCID multi-institution pattern found in 18/50 authors) is the most user-validated direction for this product to expand into next.

---

### Q6 — "If a record was flagged, what would you want to see next — a warning, a corrected score, or the raw evidence?"

**Why this question was chosen:** Directly shapes the UI decision the task requires teams to justify — this question's answer was meant to determine exactly what a flagged record's card should show.

**What we learned:** Both gave essentially the same answer, worth quoting closely: P1 wanted "the original confidence score, the explanation that caused the problem, and the evidence... so I could make the final judgment myself." P2 was even more direct: "I wouldn't want the system to just replace one unexplained number with another unexplained number." Both explicitly said a corrected score is useful *only* alongside the evidence, never as a silent replacement for it.

**How it affected the prototype:** This is the most directly build-shaping answer in either interview. It's the reason every evidence card in the prototype shows **all four elements together, with nothing hidden**: the original score (struck through), the corrected score (circled), the exact phrase that triggered the correction (highlighted inline in the reasoning text), and a plain-English explanation of why the correction was made. Early design sketches considered hiding the original score behind a toggle to reduce clutter — this answer is why that idea was dropped.

---

### Q7 — Closing / catch-all

**Why this question was chosen:** To surface anything the planned questions missed.

**What we learned:** Both raised a point neither had been directly asked about: **information about the same researcher is fragmented across platforms** (Google Scholar, LinkedIn, ORCID, university pages), and reconciling it manually is time-consuming. P2 specifically added **recency** — knowing when a piece of information was last verified, since a researcher's current focus can differ substantially from their historical record.

**How it affected the prototype:** The fragmentation point reinforced the existing scope (Scholarix's data already aggregates multiple sources — this prototype makes the *confidence* in that aggregation visible, addressing exactly this pain point). The recency point could not be built into the current prototype — the provided `broad_impact.json` records don't carry reliable per-record timestamps — so it's documented honestly as a scoping limitation and listed as a "next step" in the README rather than silently ignored.

---

## What we did *not* force to fit

Neither interviewee suggested pivoting to a different product direction (e.g. duplicate detection or a network graph) when asked directly, and neither interview surfaced evidence against the chosen direction — this is disclosed honestly rather than assumed, and should be read as a small-sample (n=2) validation, not proof the direction is optimal for all users of Scholarix AI's data.
