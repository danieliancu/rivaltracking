"""Celery tasks for scanning. Tasks take IDs only and re-resolve entities.

Beat runs ``dispatch_due_scans`` periodically; it enqueues per-competitor scan
jobs (deduped by a cache lock + active-job check) so overlapping scans of the
same competitor never run.
"""
from celery import shared_task
from django.utils import timezone

from apps.competitors.models import Competitor

from . import services
from .models import ScanJob


@shared_task(
    bind=True,
    queue="scraping",
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def run_scan_job(self, job_id):
    """Execute a single ScanJob (idempotent: no-ops if not active)."""
    return _summarise(services.execute_scan_job(job_id))


@shared_task(queue="scraping")
def dispatch_due_scans():
    """Beat entrypoint: enqueue scans for competitors whose schedule is due."""
    now = timezone.now()
    due = Competitor.objects.filter(monitoring_enabled=True).filter(
        models_next_scan_due(now)
    )
    dispatched = 0
    for competitor in due.iterator():
        if services.has_active_job(competitor):
            continue
        if not services.acquire_scan_lock(competitor.id):
            continue
        services.create_and_dispatch_scheduled(competitor)
        dispatched += 1
    return {"dispatched": dispatched}


def models_next_scan_due(now):
    from django.db.models import Q

    return Q(next_scan_at__isnull=True) | Q(next_scan_at__lte=now)


def _summarise(job):
    if job is None:
        return {"status": "skipped"}
    return {
        "job_id": job.id,
        "status": job.status,
        "changes_detected": job.changes_detected,
        "products_updated": job.products_updated,
    }
