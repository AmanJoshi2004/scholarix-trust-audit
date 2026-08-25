"""
confidence_audit.py

Core logic for the Scholarix Trust Audit prototype.

The problem this solves:
Each record in broad_impact.json carries two AI-generated signals about the
same claim: a numeric `relevance_score` (0-100) and a free-text `reasoning`
sentence explaining that score. These two signals should agree. In practice,
many records pair a near-perfect score with reasoning that hedges
("appears to be", "likely", "possibly") -- i.e. the AI's own explanation
admits uncertainty that the number does not reflect.

This module re-reads the reasoning text, detects hedging or definitive
language, and produces an *adjusted* confidence score plus a plain-English
verdict a non-technical user (e.g. a research administrator) can act on.

Design notes / limitations (documented on purpose, per task rules):
- This is a transparent, rule-based lexical audit, not a black-box model.
  Every flag can be traced back to the exact phrase that triggered it.
- It is intentionally conservative: it only flags a *contradiction* between
  stated confidence and stated certainty language, not "correctness" of the
  underlying fact (we have no ground truth for that here).
- Hedge/definitive phrase lists are a starting point, not exhaustive. They
  can be extended in HEDGE_PHRASES / DEFINITIVE_PHRASES below.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Phrase dictionaries
# ---------------------------------------------------------------------------
# Each phrase maps to a "weight" -- how strongly it signals uncertainty (or,
# for definitive phrases, certainty). Weights are additive and capped so one
# repeated phrase can't dominate the score.

HEDGE_PHRASES: dict[str, int] = {
    "appears to be": 15,
    "likely": 12,
    "probably": 12,
    "seems to": 10,
    "seemingly": 10,
    "possibly": 10,
    "could be": 8,
    "may be": 8,
    "might be": 8,
    "presumably": 10,
    "suggests": 6,
    "it is unclear": 20,
    "not certain": 20,
    "difficult to determine": 18,
    "hard to confirm": 18,
    "cannot confirm": 18,
    "unable to verify": 18,
    "seems like": 10,
    "potentially": 10,
    "could not be confirmed": 20,
    "not confirmed": 18,
    "not verified": 18,
}

DEFINITIVE_PHRASES: dict[str, int] = {
    "confirmed": 18,
    "verified": 15,
    "officially": 15,
    "definitely": 15,
    "clearly the": 12,
    "matches exactly": 15,
    "is the official": 15,
    "directly states": 12,
}

HEDGE_PENALTY_CAP = 40
DEFINITIVE_BONUS_CAP = 20

# A record only gets flagged as "Overstated" if its original score is at or
# above this bar -- low scores that also hedge are *consistent*, not a bug.
OVERSTATED_SCORE_FLOOR = 75
# A record only gets flagged as "Understated" if its original score is at or
# below this bar despite definitive language.
UNDERSTATED_SCORE_CEILING = 50


@dataclass
class AuditResult:
    url: Optional[str]
    snippet: Optional[str]
    category: Optional[str]
    reasoning: str
    original_score: int
    adjusted_score: int
    verdict: str
    severity: str
    hedge_phrases_found: list[str] = field(default_factory=list)
    definitive_phrases_found: list[str] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "snippet": self.snippet,
            "category": self.category,
            "reasoning": self.reasoning,
            "original_score": self.original_score,
            "adjusted_score": self.adjusted_score,
            "verdict": self.verdict,
            "severity": self.severity,
            "hedge_phrases_found": self.hedge_phrases_found,
            "definitive_phrases_found": self.definitive_phrases_found,
            "explanation": self.explanation,
        }


def _find_phrases(text: str, phrase_map: dict[str, int], mask: list[bool] | None = None):
    """
    Return (capped total weight, list of matched phrases, match spans) for a
    phrase map. `mask` (same length as text) marks characters already claimed
    by another phrase match, so e.g. "confirmed" inside an already-matched
    "could not be confirmed" hedge phrase is not double-counted (or
    miscounted as the opposite signal). Longer phrases are checked first so
    they claim their span before shorter overlapping phrases are tried.
    """
    text_l = text.lower()
    if mask is None:
        mask = [False] * len(text_l)

    matched = []
    total = 0
    spans: list[tuple[int, int]] = []

    for phrase in sorted(phrase_map, key=len, reverse=True):
        start = 0
        while True:
            idx = text_l.find(phrase, start)
            if idx == -1:
                break
            end = idx + len(phrase)
            if not any(mask[idx:end]):
                matched.append(phrase)
                total += phrase_map[phrase]
                for i in range(idx, end):
                    mask[i] = True
                spans.append((idx, end))
            start = idx + 1

    return total, matched, mask


def _severity_for_gap(gap: int) -> str:
    if gap >= 30:
        return "Severe"
    if gap >= 15:
        return "Moderate"
    if gap > 0:
        return "Mild"
    return "None"


def audit_record(record: dict) -> AuditResult:
    """Audit a single broad_impact.json record."""
    reasoning = record.get("reasoning") or ""
    original_score = int(record.get("relevance_score") or 0)

    # Hedge phrases are matched first and "claim" their character span, so a
    # definitive-sounding word inside a hedge phrase (e.g. "confirmed" inside
    # "could not be confirmed") isn't separately counted as definitive.
    hedge_weight, hedge_matches, mask = _find_phrases(reasoning, HEDGE_PHRASES)
    definitive_weight, definitive_matches, _ = _find_phrases(reasoning, DEFINITIVE_PHRASES, mask=mask)

    hedge_weight = min(hedge_weight, HEDGE_PENALTY_CAP)
    definitive_weight = min(definitive_weight, DEFINITIVE_BONUS_CAP)

    adjusted_score = original_score - hedge_weight + definitive_weight
    adjusted_score = max(0, min(100, adjusted_score))

    verdict = "Consistent"
    explanation = (
        "The stated confidence score matches the certainty of the AI's own "
        "explanation. No correction needed."
    )
    severity = "None"

    if hedge_matches and original_score >= OVERSTATED_SCORE_FLOOR:
        gap = original_score - adjusted_score
        severity = _severity_for_gap(gap)
        verdict = "Overstated Confidence"
        phrase_list = ", ".join(f'"{p}"' for p in hedge_matches)
        explanation = (
            f"This record was scored {original_score}/100 (near-certain), but its own "
            f"reasoning hedges with {phrase_list}. That language does not match a "
            f"near-perfect score, so the confidence has been reduced to {adjusted_score}/100."
        )
    elif definitive_matches and original_score <= UNDERSTATED_SCORE_CEILING:
        verdict = "Understated Confidence"
        severity = "Mild" if (adjusted_score - original_score) < 15 else "Moderate"
        phrase_list = ", ".join(f'"{p}"' for p in definitive_matches)
        explanation = (
            f"This record was scored only {original_score}/100, but its reasoning uses "
            f"definitive language such as {phrase_list}. The evidence sounds more certain "
            f"than the score suggests, so confidence has been raised to {adjusted_score}/100."
        )
    elif hedge_matches:
        explanation = (
            "The reasoning hedges, and the original score is already low/moderate, so "
            "the score is honest about its own uncertainty. No correction needed."
        )

    return AuditResult(
        url=record.get("url"),
        snippet=record.get("snippet"),
        category=record.get("category"),
        reasoning=reasoning,
        original_score=original_score,
        adjusted_score=adjusted_score,
        verdict=verdict,
        severity=severity,
        hedge_phrases_found=hedge_matches,
        definitive_phrases_found=definitive_matches,
        explanation=explanation,
    )


def audit_records(records: list[dict]) -> list[AuditResult]:
    return [audit_record(r) for r in records]


def summarize(results: list[AuditResult]) -> dict:
    total = len(results)
    consistent = sum(1 for r in results if r.verdict == "Consistent")
    overstated = sum(1 for r in results if r.verdict == "Overstated Confidence")
    understated = sum(1 for r in results if r.verdict == "Understated Confidence")

    avg_gap = 0.0
    flagged = [r for r in results if r.verdict != "Consistent"]
    if flagged:
        avg_gap = sum(abs(r.original_score - r.adjusted_score) for r in flagged) / len(flagged)

    by_category: dict[str, dict[str, int]] = {}
    for r in results:
        cat = r.category or "Unknown"
        by_category.setdefault(cat, {"total": 0, "overstated": 0, "understated": 0})
        by_category[cat]["total"] += 1
        if r.verdict == "Overstated Confidence":
            by_category[cat]["overstated"] += 1
        elif r.verdict == "Understated Confidence":
            by_category[cat]["understated"] += 1

    return {
        "total_records": total,
        "consistent": consistent,
        "overstated": overstated,
        "understated": understated,
        "consistent_pct": round(100 * consistent / total, 1) if total else 0,
        "overstated_pct": round(100 * overstated / total, 1) if total else 0,
        "understated_pct": round(100 * understated / total, 1) if total else 0,
        "avg_adjustment_when_flagged": round(avg_gap, 1),
        "by_category": by_category,
    }
