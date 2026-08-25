# Customer Interview Guide — Scholarix Trust Audit

This guide is for the 2 required user interviews. It's built around one core script that works across all four persona types you're considering (grad student, faculty/PI, research admin, librarian), with persona-specific probes you can swap in. Pick your 2 real interviewees from *different* persona types if possible — that gives you two genuinely different perspectives to compare in your report, which is worth more than two similar ones.

**Target: 20–30 minutes per interview.** Record with permission if possible, or take detailed notes — you'll need direct quotes/paraphrases for the interview report.

---

## Before you start: picking interviewees

Good candidates for the 4 persona types you're considering:
- **Grad student / PhD researcher** — someone who regularly searches for potential advisors, collaborators, or comparable labs
- **Faculty / PI** — someone who reviews grant applications, sits on hiring/tenure committees, or vets potential collaborators
- **Research admin / program staff** — someone who compiles faculty reports, verifies CVs for grant submissions, or maintains institutional researcher directories
- **Librarian** — someone who does citation/bibliometric work, or helps researchers verify their own profiles (e.g. ORCID, Scopus)

You don't need to lock in the persona before reaching out — the same core questions work for any of them. Let the conversation tell you which persona this person actually is.

---

## Opening (2 min, don't record as a "finding")

Briefly explain: *"We're building a small tool that checks whether AI-generated confidence scores on researcher data actually match the reasoning behind them. I want to understand how you currently use or evaluate researcher information, and what would make you trust or distrust it."* Don't lead them toward your specific solution yet — the goal of the first half is to hear their problem in their own words before you describe yours.

---

## Core question set

### 1. "Walk me through the last time you looked someone up — a researcher, potential collaborator, or candidate. What were you trying to find out, and where did you look?"

**Why this question:** Opens with their real behavior, not a hypothetical. Tests the basic assumption that this persona actually does researcher lookups often enough to have a real workflow — if they can't easily answer this, they may not be relevant to your product.
**What you're listening for:** which sources they trust already (Google Scholar, ORCID, a university directory, LinkedIn), and whether they cross-check multiple sources or take the first result at face value.

### 2. "Has a piece of information about a researcher — an affiliation, a citation count, a publication — ever turned out to be wrong or outdated? What happened?"

**Why this question:** Tests whether "bad data" is a real, felt problem for them or just a hypothetical concern. A concrete story here is much stronger evidence than a hypothetical "yes I guess that could be an issue."
**What you're listening for:** what *kind* of error mattered to them (stale affiliation vs. wrong citation count vs. mixed-up identity) — this tells you which of the data problems you found is worth prioritizing.

### 3. "When you see a score, rating, or 'confidence' label attached to information — like a relevance score, a match percentage, a verification badge — how much do you trust it? Do you ever check the reasoning behind it, or just the number?"

**Why this question:** This is the single most important question for your specific direction. It directly tests your core hypothesis: that people anchor on the number and skip the explanation. If they say "I always read the reasoning," that's a real signal your correction-layer approach may need to surface differently (e.g., inline warnings, not just an audit report).
**What you're listening for:** an honest admission that they skim/trust scores more than they'd like to admit — or evidence you're wrong and they're already skeptical of scores, which changes how you'd pitch the tool.

### 4. "If I showed you two records — one where an AI said '100% confident' and explained its reasoning clearly, and another where it also said '100% confident' but the explanation was full of hedging like 'appears to be' or 'likely' — would that difference matter to you? Why or why not?"

**Why this question:** This tests the actual product concept directly, without naming your solution yet. It's the closest thing to a concept test you can do in an interview. A weak or confused reaction here is a real signal to take seriously, not something to talk them out of.
**What you're listening for:** do they immediately get why that's a problem, or do they need convincing? Also listen for their own vocabulary — use their words, not yours, in your product brief.

### 5. "What would it take for you to stop trusting a researcher-data tool? What's the line between 'this has some rough edges' and 'I can't use this anymore'?"

**Why this question:** Surfaces their actual trust threshold, which tells you how aggressively your tool needs to flag problems and how much explanation is enough vs. overkill.
**What you're listening for:** specific, concrete failure conditions (e.g. "if I catch it being wrong about someone I know personally, I stop trusting the whole system") — these become your prototype's design constraints.

### 6. "If a tool flagged a record as 'the AI's confidence doesn't match its own reasoning here' — what would you want to see next? Just a warning? A corrected score? A way to see the original evidence and decide yourself?"

**Why this question:** Directly shapes your prototype's UI decisions (which is required — you must show what you built *because of* the interview). Their answer determines whether your evidence cards should default to showing the correction, or hide it behind a click, or something else.
**What you're listening for:** do they want to be told what to think (corrected score) or given the raw material to judge themselves (just show me the evidence)? This is a real design fork — capture their exact preference.

### 7. Closing: "Is there anything about how you currently evaluate researcher data that I haven't asked about, but that's actually a bigger problem for you than what we've discussed?"

**Why this question:** A catch-all in case your question set missed their real pain point. Sometimes the most useful insight in an interview is the thing you didn't think to ask about.

---

## Persona-specific probes (optional, use 1–2 if time allows)

**Grad student:** *"When you're searching for a potential advisor or collaborator, does a wrong or outdated profile ever cause you to waste time — e.g. reaching out to someone who's actually moved institutions?"*

**Faculty / PI:** *"When you're on a hiring or grant review committee, how much do you personally re-verify a candidate's claimed metrics versus trusting what's provided?"*

**Research admin:** *"When you're compiling a faculty report or grant submission, what's your process for catching an error before it goes out under your institution's name?"*

**Librarian:** *"Do researchers ever come to you specifically to fix or dispute something wrong in their public profile? What's that conversation usually like?"*

---

## After the interview: filling in the required deliverable

For each interview, the task requires this exact structure (Section 5/9 of the task doc) — fill this in right after each interview while it's fresh:

| Field | What to write |
|---|---|
| Who they are | Role, context, why relevant to Scholarix AI |
| Issue they faced | The concrete story from Q2 |
| Why they'd use this | Their answer to Q3/Q4, in their own words |
| Features they want | Their answer to Q6 |
| Trust concerns | Their answer to Q5 |
| Product implications | What you decided to build/change because of this — be specific, e.g. "P1 said they want to see raw evidence, not just a corrected number, so we kept both the original and adjusted score visible side-by-side instead of hiding the original." |

And for the **interview question rationale** deliverable, you already have "why this question was chosen" written above for each question — after the interview, add a "what you learned" and "how it affected the prototype" line per question, using the actual answer you got.

---

## A note on honesty in this document

Don't force-fit your interview answers into confirming what you already built. If an interviewee doesn't care about the confidence/reasoning gap, or explicitly says they'd rather see something else (e.g. duplicate detection, or a network view), write that down honestly and explain in your product brief why you still chose this direction (e.g. "this was true for 1 of 2 interviewees, and separately supported by the data patterns we found") — evaluators are explicitly told to look for honest tradeoffs, not a tidy story where everything lines up perfectly.
