"""Celery application for RivalTracking's Phase 3 processing engine.

One Celery app, several queues (see ``CELERY_TASK_ROUTES`` in settings):
``scraping``, ``processing``, ``matching``, ``ai``, ``alerts``, ``reports``.
Tasks live in each app's ``tasks.py`` and are autodiscovered.
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("rivaltracking")
# All Celery config comes from Django settings, namespaced CELERY_*.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):  # pragma: no cover - operational helper
    print(f"Request: {self.request!r}")
