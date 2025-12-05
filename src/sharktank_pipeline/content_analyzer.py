"""Transcript processing and business rubric scoring."""

from __future__ import annotations

import re
from typing import Dict, Sequence

from .models import ContentMetrics


PITCH_STAGES = ("Hook", "Problem", "Solution", "Ask")


def _normalized_score(raw: float, max_points: float = 100.0) -> float:
    return float(max(0.0, min(max_points, raw)))


def _keyword_score(transcript: str, keywords: Sequence[str], weight: float = 1.0) -> float:
    matches = sum(1 for keyword in keywords if keyword in transcript)
    return _normalized_score(matches / max(1, len(keywords)) * 100 * weight)


def detect_pitch_structure(transcript: str) -> Sequence[str]:
    transcript_lower = transcript.lower()
    detected = []
    if any(token in transcript_lower for token in ["imagine", "picture", "what if"]):
        detected.append("Hook")
    if any(token in transcript_lower for token in ["problem", "pain", "struggle", "challenge"]):
        detected.append("Problem")
    if any(token in transcript_lower for token in ["solution", "we built", "product", "platform"]):
        detected.append("Solution")
    if any(token in transcript_lower for token in ["ask", "raise", "investment", "seeking"]):
        detected.append("Ask")
    return detected


def rubric_scores(transcript: str) -> Dict[str, float]:
    transcript_lower = transcript.lower()

    problem_clarity = _keyword_score(transcript_lower, ["problem", "pain", "issue", "need"], weight=1.2)
    differentiation = _keyword_score(transcript_lower, ["unique", "differentiated", "defensible", "moat"])
    business_model = _keyword_score(transcript_lower, ["model", "pricing", "subscription", "margin"], weight=1.1)
    market_opportunity = _keyword_score(transcript_lower, ["market", "tam", "sam", "growth"], weight=1.1)
    revenue_logic = _keyword_score(transcript_lower, ["revenue", "pricing", "customers", "arpu"], weight=1.0)
    competition_awareness = _keyword_score(transcript_lower, ["competitor", "competition", "alternative", "incumbent"])

    return {
        "problem_clarity": problem_clarity,
        "differentiation": differentiation,
        "business_model": business_model,
        "market_opportunity": market_opportunity,
        "revenue_logic": revenue_logic,
        "competition_awareness": competition_awareness,
    }


def score_business(scores: Dict[str, float]) -> float:
    weighted = (
        scores["market_opportunity"] * 0.25
        + scores["revenue_logic"] * 0.25
        + scores["differentiation"] * 0.2
        + scores["competition_awareness"] * 0.15
        + scores["problem_clarity"] * 0.15
    )
    return float(min(100.0, max(0.0, weighted)))


def analyze_content(transcript: str) -> ContentMetrics:
    """Run NLP rubric scoring and structure detection over the transcript."""

    cleaned = re.sub(r"\s+", " ", transcript).strip()
    rubric = rubric_scores(cleaned)
    structure = detect_pitch_structure(cleaned)
    business_score = score_business(rubric)

    return ContentMetrics(
        problem_clarity=rubric["problem_clarity"],
        differentiation=rubric["differentiation"],
        business_model=rubric["business_model"],
        market_opportunity=rubric["market_opportunity"],
        revenue_logic=rubric["revenue_logic"],
        competition_awareness=rubric["competition_awareness"],
        pitch_structure=structure,
        business_score=business_score,
        transcript=cleaned,
    )

