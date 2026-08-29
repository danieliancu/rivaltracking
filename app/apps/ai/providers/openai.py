"""OpenAI-backed provider (opt-in via AI_PROVIDER=openai + OPENAI_API_KEY).

Operates only on structured data RivalTracking already computed — never raw
scraped pages. Falls back to the deterministic stub on any error so AI issues
never break the pipeline.
"""
from __future__ import annotations

import json

from django.conf import settings

from .base import AIProvider, ChangeInsight
from .stub import StubProvider

_ANALYSIS_SYSTEM = (
    "You are a competitor-pricing analyst. Given a single structured change "
    "event, respond with concise JSON: {summary, why_it_matters, "
    "recommended_action, confidence (0-1), urgency (high|medium|low), "
    "supporting_points (array of short strings)}. Base everything only on the "
    "provided fields."
)


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self):
        self._stub = StubProvider()
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI  # lazy import

            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    def _chat_json(self, system, payload):
        client = self._get_client()
        resp = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload)},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return json.loads(resp.choices[0].message.content)

    def analyse_change(self, event_data) -> ChangeInsight:
        try:
            data = self._chat_json(_ANALYSIS_SYSTEM, event_data)
            return ChangeInsight(
                summary=data.get("summary", ""),
                why_it_matters=data.get("why_it_matters", ""),
                recommended_action=data.get("recommended_action", ""),
                confidence=float(data.get("confidence", 0.5)),
                urgency=data.get("urgency", "medium"),
                supporting_points=data.get("supporting_points", []),
            )
        except Exception:
            return self._stub.analyse_change(event_data)

    def answer_question(self, workspace, question, context=None):
        # Ask AI keeps the structured card; the deterministic corpus provides the
        # shape and a real narrative is layered in from structured tool data.
        base = self._stub.answer_question(workspace, question, context)
        try:
            from apps.ai import tools

            facts = tools.answer_context(workspace, question, context or {})
            narrative = self._chat_json(
                "You are a competitor-intelligence assistant. Answer the user's "
                "question in 2-3 sentences using only the provided workspace facts. "
                'Respond as JSON {"summary": "..."}.',
                {"question": question, "facts": facts},
            )
            if narrative.get("summary"):
                base = dict(base)
                base["summary"] = narrative["summary"]
        except Exception:
            pass
        return base

    def summarise_period(self, workspace, stats) -> str:
        try:
            data = self._chat_json(
                'Summarise these competitor-intelligence stats in 2 sentences. JSON {"summary": "..."}.',
                stats,
            )
            return data.get("summary") or self._stub.summarise_period(workspace, stats)
        except Exception:
            return self._stub.summarise_period(workspace, stats)

    def explain_competitor(self, workspace, competitor_data) -> str:
        return self._stub.explain_competitor(workspace, competitor_data)

    def generate_report_summary(self, workspace, report_data) -> str:
        try:
            data = self._chat_json(
                'Write a 3-sentence executive summary of this competitor report. JSON {"summary": "..."}.',
                report_data,
            )
            return data.get("summary") or self._stub.generate_report_summary(workspace, report_data)
        except Exception:
            return self._stub.generate_report_summary(workspace, report_data)
