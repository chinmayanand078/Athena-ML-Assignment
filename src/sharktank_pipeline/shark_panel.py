"""Virtual shark persona feedback generation."""

from dataclasses import dataclass
from typing import Dict, List

from .models import ContentMetrics, DeliveryMetrics, PanelResponse, SharkFeedback


@dataclass
class SharkPersona:
    name: str
    focus: str
    tone: str

    def render_feedback(self, delivery: DeliveryMetrics, content: ContentMetrics) -> SharkFeedback:
        strengths = []
        weaknesses = []

        if delivery.delivery_score > 75:
            strengths.append("strong delivery energy")
        if content.business_score > 70:
            strengths.append("compelling business fundamentals")
        if "Ask" in content.pitch_structure:
            strengths.append("clear fundraising ask")

        if delivery.pause_ratio > 0.25:
            weaknesses.append("too many pauses")
        if delivery.filler_count > 5:
            weaknesses.append("filler words reduce clarity")
        if content.competition_awareness < 40:
            weaknesses.append("competition strategy is light")

        summary_parts = []
        if strengths:
            summary_parts.append(f"Strengths: {', '.join(strengths)}.")
        if weaknesses:
            summary_parts.append(f"Weaknesses: {', '.join(weaknesses)}.")

        persona_line = (
            f"As {self.name} ({self.focus}), I see delivery at {delivery.delivery_score:.0f}/100 "
            f"and business at {content.business_score:.0f}/100. "
            + " ".join(summary_parts)
        )

        recommendation = "Invest" if content.business_score > 80 and delivery.delivery_score > 75 else "Need More Info"
        return SharkFeedback(persona=self.name, tone=self.tone, content=persona_line, recommendation=recommendation)


def default_panel() -> List[SharkPersona]:
    return [
        SharkPersona(name="The Visionary", focus="innovation & market scale", tone="Optimistic and future-focused"),
        SharkPersona(name="The Finance Shark", focus="unit economics & revenue", tone="Direct and numbers-driven"),
        SharkPersona(name="The Customer Advocate", focus="user pain & adoption", tone="Empathetic and pragmatic"),
        SharkPersona(name="The Skeptic", focus="risks & defensibility", tone="Challenging and incisive"),
    ]


def run_panel(delivery: DeliveryMetrics, content: ContentMetrics, personas: List[SharkPersona] | None = None) -> PanelResponse:
    if personas is None:
        personas = default_panel()

    feedback = [persona.render_feedback(delivery, content) for persona in personas]
    recommendations = [item.recommendation for item in feedback if item.recommendation]

    if recommendations.count("Invest") >= 2:
        final_recommendation = "Invest"
    elif "Need More Info" in recommendations:
        final_recommendation = "Need More Info"
    else:
        final_recommendation = "Not Invest"

    return PanelResponse(delivery=delivery, content=content, feedback=feedback, final_recommendation=final_recommendation)

