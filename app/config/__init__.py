"""Ensure the Celery app is loaded when Django starts (for shared_task use)."""
from .celery import app as celery_app

__all__ = ("celery_app",)
