"""Generic adapter — the default deterministic path (JSON-LD → DOM)."""
from .base import Adapter


class GenericAdapter(Adapter):
    name = "generic"

    @staticmethod
    def detect(fetch_result) -> bool:
        return True  # always applicable as the fallback
