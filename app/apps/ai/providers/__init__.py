"""AI provider factory. Default is the deterministic stub (no API key needed)."""
from functools import lru_cache

from django.conf import settings

from .base import AIProvider, ChangeInsight
from .stub import StubProvider

__all__ = ["AIProvider", "ChangeInsight", "get_provider"]


@lru_cache(maxsize=2)
def _provider_for(name, has_key):
    if name == "openai" and has_key:
        from .openai import OpenAIProvider

        return OpenAIProvider()
    return StubProvider()


def get_provider() -> AIProvider:
    return _provider_for(settings.AI_PROVIDER, bool(settings.OPENAI_API_KEY))
