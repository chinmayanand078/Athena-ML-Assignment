"""Data models used across the Shark Tank pitch analyzer pipelines."""

from dataclasses import dataclass, field
from typing import List, Optional, Sequence


@dataclass
class DeliveryMetrics:
    """Metrics describing vocal delivery extracted from the audio signal."""

    pitch_mean: float
    pace_wpm: float
    volume_variance: float
    pause_ratio: float
    filler_count: int
    monotony_score: float
    emotion: str
    delivery_score: float


@dataclass
class ContentMetrics:
    """Scores derived from the pitch transcript and business rubric."""

    problem_clarity: float
    differentiation: float
    business_model: float
    market_opportunity: float
    revenue_logic: float
    competition_awareness: float
    pitch_structure: Sequence[str]
    business_score: float
    transcript: str


@dataclass
class SharkFeedback:
    """Feedback from a single shark persona."""

    persona: str
    tone: str
    content: str
    recommendation: Optional[str] = None


@dataclass
class PanelResponse:
    """Combined response from the full virtual shark panel."""

    delivery: DeliveryMetrics
    content: ContentMetrics
    feedback: List[SharkFeedback] = field(default_factory=list)
    final_recommendation: str = "Need More Info"

