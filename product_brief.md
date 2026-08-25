# Product Brief — Scholarix Trust Audit

## The problem

Scholarix AI's researcher data pipeline generates AI-based confidence scores to help users quickly judge how relevant or trustworthy a piece of information is. We found that in **42.6% of the `broad_impact.json` records we audited (146 of 343, across all 50 provided authors), the AI's own stated confidence score contradicts the certainty expressed in its own reasoning text** — a record can be scored 95–100/100 while the reasoning explaining that score hedges with "appears to be," "likely," or "possibly."

This is not a data-collection failure — the underlying information itself may well be correct. It's a **self-consistency failure**: the number and the explanation behind it don't agree, and most users only read the number.

## Why this matters, in users' own words

We interviewed two graduate students who regularly evaluate researcher information (see Customer Interview Report for full detail). Both, independently, described the same behavior pattern:

> "If I see something like a high match percentage or confidence score, my first reaction is to trust it... But if the information is important... I'd want to understand why the system gave that score." — P1 (Aditya)

> "I pay attention to the score first because it's an easy way to quickly compare results... But I wouldn't completely trust the number if the decision were important." — P2 (Daksh)

Both confirmed, unprompted, that a high score paired with hedged reasoning would make them question the score — validating that this contradiction isn't just a data-integrity curiosity, it's something real users notice and are bothered by once they see it.

## Target users

Primary: people who use aggregated researcher data to make a decision — deciding who to contact, cite, hire, fund, or collaborate with. Our interviewees (grad students evaluating potential advisors/collaborators) are a direct proxy for the broader set of users this generalizes to: research administrators compiling reports, grant panelists screening applicants, hiring committees, and librarians fielding profile-accuracy questions — all of whom described the same "trust the score when skimming, verify when it matters" pattern in some form during the broader task's suggested user list.

## Chosen product direction

**A confidence-audit layer that reconciles an AI-generated score against the certainty expressed in its own explanation, and shows the user both the correction and the exact evidence behind it — never a silent replacement.**

We explicitly did **not** build a duplicate-detector, a network graph, or a general "flag bad data" tool, even though we found real evidence for issues those directions could address (see Data Validation Report). We chose this direction because:
1. It's the only issue in the dataset that is a *pure self-contradiction* — no external ground truth or source-coverage nuance is needed to detect it (unlike citation-count disagreement, which requires understanding what each source actually indexes).
2. It was the direction most directly and immediately validated by both interviews — neither interviewee needed convincing when we described the concept (Q4).
3. It's narrow enough to build and explain well in the available time, per the task's explicit preference for a focused solution over a broad, unfinished one.

## Feature prioritization

| Feature | Priority | Why |
|---|---|---|
| Score-vs-reasoning contradiction detection | P0 — built | The core mechanism; everything else depends on it |
| Transparent, phrase-level explanation ("this exact phrase triggered the correction") | P0 — built | Both interviewees explicitly rejected an unexplained corrected score |
| Original score + corrected score shown together, never one replacing the other | P0 — built | Direct requirement from both interviews (Q6) |
| Aggregate dashboard (ledger stats, sortable researcher table) | P1 — built | Supports the "skim mode" half of the trust pattern both users described |
| Per-researcher drill-down with full evidence per claim | P1 — built | Supports the "decision mode" half of the trust pattern |
| "Worst offenders" view across all researchers | P2 — built | Useful for a reviewer auditing the pipeline itself, not just one profile |
| Identity/affiliation-collision detection | P1 for next iteration — **not built** | Named by both interviewees as the #1 trust-breaker; out of scope for this prototype (see tradeoffs) |
| Recency / last-verified timestamps | P2 for next iteration — **not built** | Raised unprompted by P2; not buildable with current data (no reliable per-record timestamps) |
| Citation cross-source reconciliation | Deprioritized | Requires modeling each source's actual coverage (see Data Validation Report, Issue 2) — a two-week prototype can't responsibly resolve this without risking a worse error than the one it's fixing |

## User stories & acceptance criteria

**Story 1:** *As a user skimming many researcher records, I want to see at a glance how much of the data I can trust, so I know whether to slow down and check further.*
- ✅ Acceptance: the dashboard shows a total-claims / consistent / overstated / understated breakdown immediately on load, with no click required.

**Story 2:** *As a user relying on a specific claim about a researcher, I want to see whether the AI's stated confidence actually matches its own reasoning, so I don't get misled by an inflated score.*
- ✅ Acceptance: every claim shows its original score, and if flagged, an adjusted score plus the specific phrase that triggered the adjustment.

**Story 3:** *As a user who doesn't trust a corrected score blindly, I want to see the original evidence, not just the tool's opinion, so I can make my own judgment.*
- ✅ Acceptance: the original score, the source URL/snippet, and the full reasoning text (with the triggering phrase highlighted) are always shown together — never replaced or hidden.

**Story 4:** *As a reviewer auditing the pipeline itself (not one researcher), I want to see which researchers or categories have the most overstated claims, so I know where the pipeline is least reliable.*
- ✅ Acceptance: the "All Researchers" table is sortable by overstated count, and a "Worst Offenders" view surfaces the most severe individual cases across the whole dataset.

## Tradeoffs

- **We chose depth over breadth.** The prototype does one thing — confidence/reasoning reconciliation — very thoroughly, rather than attempting all five data issues found in the Data Validation Report shallowly.
- **We chose transparency over automation.** The tool never silently "fixes" data; it always shows its work. This was a direct response to interview feedback, but it does mean the tool asks more of the user (reading the reasoning) than a tool that just presented a single trust score would.
- **We left the most-requested feature (identity-collision detection) unbuilt.** This was a deliberate scope decision, not an oversight — building it well would require a second, differently-shaped audit (comparing institution lists and name patterns, not text hedging), and doing it shallowly in the time remaining would have produced exactly the "broad, unfocused" result the task asks teams to avoid. It's documented as the clear next priority.
- **We chose not to attempt citation-source reconciliation** even though it's the largest single number in our data findings (90% of publications). Building a "corrected" citation count without properly modeling each source's coverage model risks introducing a new, confidently-wrong number — which would be a direct contradiction of the entire premise of this product. We considered this the right call even though it's likely the most visually impressive statistic to present, and we noted the appropriate skepticism in the Data Validation Report.

## What we'd build next

1. Identity/affiliation-collision detection (highest-validated next feature, per interviews)
2. Recency/last-verified indicators, if Scholarix's underlying data can support reliable timestamps
3. Extending the same reconciliation logic to `publications.json`'s `deep_verification` fields
4. A human-in-the-loop review action (accept/override a correction), turning this from a read-only audit into a workflow tool
