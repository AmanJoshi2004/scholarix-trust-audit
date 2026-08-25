# Customer Interview Report — Scholarix Trust Audit

Two interviews were conducted to validate the "AI Confidence Auditor" product direction before and during prototype development. Both interviewees were selected as realistic users of researcher-discovery workflows: graduate students who regularly evaluate researcher profiles when considering advisors, collaborators, or people to contact for their own academic/professional work.

---

## Interview 1

| Field | Detail |
|---|---|
| **Who they are** | Aditya (P1), second-year MSIM (Master of Science in Information Management) student. Relevant to Scholarix AI because he regularly searches for and evaluates researchers when scoping projects — a realistic proxy for the kind of researcher-discovery user Scholarix AI's data ultimately serves. |
| **Issue they faced** | Found a researcher whose Google Scholar profile still showed a previous university affiliation, while LinkedIn and the researcher's current university page showed they had moved. He also noticed citation counts varying between sources. This forced him to stop trusting any single source and cross-check manually. |
| **Why they'd use this** | He described a two-speed trust pattern: when scanning quickly, he trusts a high score at face value; but when a decision actually matters (e.g. deciding whether to reach out to someone, or using the info for a project), he wants to understand *why* the system is confident, not just see the number. A tool that already does that reconciliation for him would save the manual cross-checking he currently does by hand. |
| **Features they want** | Not just a warning — he explicitly wants to see (1) the original confidence score, (2) the exact explanation/reasoning that caused the flag, and (3) the underlying evidence/source, so he can make the final judgment himself rather than being told what to conclude. A corrected score is useful as an additional signal, but only alongside the evidence, never as a replacement for it. |
| **Trust concerns** | Identity mix-ups (two researchers with similar names conflated) were, in his words, the biggest issue — because if identity is wrong, "I wouldn't know whether the publications and other information actually belong to the right person." Outdated affiliations and confident scores attached to clearly uncertain information were the other two repeated failure modes. |
| **Product implications** | Directly confirmed the core hypothesis: users anchor on the score when skimming, but want the reasoning surfaced when it matters — validating a correction *layer* (score + evidence + explanation together) over a tool that silently replaces one opaque number with another. We kept the original score, the corrected score, and the exact triggering phrase all visible in the same view rather than hiding any of them, specifically because of this answer. |

---

## Interview 2

| Field | Detail |
|---|---|
| **Who they are** | Daksh (P2), MSFE (Master of Science in Financial Engineering) student. Relevant because he evaluates researchers/experts (e.g. in financial modeling and ML) before deciding whether to reach out — a decision-driven use case where being wrong has a real cost, similar to how a grant panel or hiring committee would use Scholarix AI's data. |
| **Issue they faced** | Found a researcher whose older papers/search results were still tied to a previous university, while their current university profile showed they had moved. Also observed publication and citation counts differing across platforms — not damaging on its own, but enough to make him verify rather than trust the first result. |
| **Why they'd use this** | Coming from a quantitative background, he was explicit that a "100% confident" claim should be reserved for genuinely strong evidence — over-claimed certainty actively bothers him more than an honest lower score would. He'd use a tool that reconciles stated confidence against actual evidence because it matches how he already reasons about uncertainty professionally. |
| **Features they want** | The flag/warning itself, but shown next to the specific part of the reasoning that contradicts the score, plus the supporting sources. He was explicit that a corrected score alone is not enough — "I wouldn't want the system to just replace one unexplained number with another unexplained number." He also raised **recency** as a feature he wants but wasn't directly asked about: knowing when a piece of information was last verified, since a researcher's current focus can differ substantially from their historical publication record. |
| **Trust concerns** | Repeated confident-but-wrong outputs, especially two people with similar names/research areas being conflated, would push him to stop trusting the tool and re-verify everything himself — "the tool wouldn't really be saving me much time" at that point. |
| **Product implications** | Reinforced the same design decision as Interview 1 (show score + evidence + explanation together, never a silent replacement), and surfaced a specific enhancement not in the original design: **recency/last-verified timestamps**. This is noted as a "next step" in the README rather than built into this prototype, since the provided `broad_impact.json` data doesn't include reliable per-record timestamps to build this on top of within the current scope — but it directly shaped what we'd prioritize next. |

---

## Cross-interview synthesis

Both interviewees, independently and using different vocabulary, converged on the same three points:

1. **A score is trusted by default when skimming, but distrusted the moment a decision matters** — which is exactly the failure mode this prototype targets: catching the gap between a stated score and what the AI's own reasoning actually supports, before the user has to notice it themselves.
2. **A "corrected" score alone is not a solution — it must come with the evidence.** Neither interviewee wanted to be told what to believe; both wanted the original score, the corrected score, and the reasoning that caused the change, together. This directly shaped the evidence-card design: original score (struck through) → corrected score (circled) → highlighted phrase → plain-English explanation, all in one card, nothing hidden behind a click.
3. **Identity/affiliation mix-ups are the single biggest trust-breaker**, more than any other error type mentioned. This is a validated direction for future work (see README "Next steps"), even though it wasn't the focus of this prototype's scope.

Neither interviewee suggested a fundamentally different direction (e.g. a duplicate detector or network graph) when asked directly — both engaged immediately and concretely with the confidence/reasoning-contradiction concept in Question 4, which is treated here as a genuine (if small, n=2) validation signal rather than assumed in advance.
