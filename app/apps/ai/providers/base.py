"""AIProvider interface. Application code depends on this, never on a vendor."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ChangeInsight:
    summary: str = ""
    why_it_matters: str = ""
    recommended_action: str = ""
    confidence: float = 0.0
    urgency: str = "medium"
    supporting_points: list = field(default_factory=list)


class AIProvider:
    name = "base"

    def answer_question(self, workspace, question, context=None):  # -> structured response dict
        raise NotImplementedError

    def analyse_change(self, event_data) -> ChangeInsight:
        raise NotImplementedError

    def summarise_period(self, workspace, stats) -> str:
        raise NotImplementedError

    def explain_competitor(self, workspace, competitor_data) -> str:
        raise NotImplementedError

    def generate_report_summary(self, workspace, report_data) -> str:
        raise NotImplementedError
