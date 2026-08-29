"""Deterministic AI provider (default). No external calls; keeps demo/tests
offline while exercising the same interface a real provider implements."""
from __future__ import annotations

from .base import AIProvider, ChangeInsight


class StubProvider(AIProvider):
    name = "stub"

    def answer_question(self, workspace, question, context=None):
        # Reuse the deterministic structured-answer corpus so the Ask AI UI is
        # unchanged; the tools layer still enforces workspace scope for any real
        # data the caller injects into context.
        from apps.ai.services import resolve_response

        return resolve_response(question, context or {})

    def analyse_change(self, event_data) -> ChangeInsight:
        etype = event_data.get("event_type", "")
        pct = event_data.get("change_percent")
        product = event_data.get("product", "This product")
        competitor = event_data.get("competitor", "the competitor")
        if etype == "price_decrease":
            return ChangeInsight(
                summary=f"{competitor} cut the price of {product} by {abs(pct or 0):.1f}%.",
                why_it_matters="A price cut of this size can shift demand toward the competitor, especially on matched products where you are now more expensive.",
                recommended_action="Review your price on the matched product and decide whether to respond.",
                confidence=0.7,
                urgency="high" if abs(pct or 0) >= 15 else "medium",
                supporting_points=[
                    f"Old price: {event_data.get('old_price')}",
                    f"New price: {event_data.get('new_price')}",
                    f"Our price: {event_data.get('our_price', 'n/a')}",
                ],
            )
        if etype == "stock_out":
            return ChangeInsight(
                summary=f"{product} is now out of stock at {competitor}.",
                why_it_matters="Competitor stock-outs are an opportunity to capture demand while they cannot fulfil it.",
                recommended_action="Ensure your equivalent product is in stock and well-positioned.",
                confidence=0.65, urgency="medium",
            )
        if etype == "promotion_started":
            return ChangeInsight(
                summary=f"{competitor} started a promotion on {product}.",
                why_it_matters="Promotions can pull share quickly; watch for a broader campaign.",
                recommended_action="Assess whether a matching or targeted promotion is warranted.",
                confidence=0.6, urgency="medium",
            )
        return ChangeInsight(
            summary=f"{product} changed at {competitor}.",
            why_it_matters="Tracked for context.",
            recommended_action="No action required.",
            confidence=0.4, urgency="low",
        )

    def summarise_period(self, workspace, stats) -> str:
        return (
            f"Over the period, {stats.get('changes', 0)} changes were detected "
            f"({stats.get('price_decreases', 0)} price cuts, "
            f"{stats.get('price_increases', 0)} rises, "
            f"{stats.get('stock_changes', 0)} stock moves)."
        )

    def explain_competitor(self, workspace, competitor_data) -> str:
        return (
            f"{competitor_data.get('name', 'This competitor')} has "
            f"{competitor_data.get('products', 0)} monitored products with "
            f"{competitor_data.get('changes_today', 0)} changes today."
        )

    def generate_report_summary(self, workspace, report_data) -> str:
        return (
            f"This period saw {report_data.get('total_changes', 0)} tracked changes across "
            f"{report_data.get('competitors', 0)} competitors. "
            "Key movements are detailed in the sections below."
        )
