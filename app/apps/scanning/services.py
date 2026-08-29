"""Scan orchestration services (framework only in this commit; the real
fetch/extract/normalise/persist pipeline is wired in the next commit)."""
from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.competitors.models import Competitor

from .models import ScanJob

FREQUENCY_HOURS = {
    "Every 24 hours": 24,
    "Every 12 hours": 12,
    "Every 6 hours": 6,
}
DEFAULT_FREQUENCY_HOURS = 24

# How long a per-competitor scan lock is held (seconds) to prevent overlap.
SCAN_LOCK_TTL = 3600


def next_scan_time(competitor, now=None):
    now = now or timezone.now()
    hours = FREQUENCY_HOURS.get(competitor.monitoring_frequency, DEFAULT_FREQUENCY_HOURS)
    return now + timedelta(hours=hours)


def _lock_key(competitor_id):
    return f"scan-lock:competitor:{competitor_id}"


def acquire_scan_lock(competitor_id):
    """Atomic-ish lock via the cache. Returns True if acquired."""
    return cache.add(_lock_key(competitor_id), "1", SCAN_LOCK_TTL)


def release_scan_lock(competitor_id):
    cache.delete(_lock_key(competitor_id))


def has_active_job(competitor):
    return ScanJob.objects.filter(
        competitor=competitor, status__in=[ScanJob.Status.QUEUED, ScanJob.Status.RUNNING]
    ).exists()


@transaction.atomic
def create_scan_job(competitor, *, trigger=ScanJob.Trigger.MANUAL):
    return ScanJob.objects.create(
        workspace=competitor.workspace,
        competitor=competitor,
        trigger_type=trigger,
        status=ScanJob.Status.QUEUED,
    )


def create_and_dispatch_scheduled(competitor):
    """Used by the beat dispatcher (which already holds the scan lock)."""
    from . import tasks

    job = create_scan_job(competitor, trigger=ScanJob.Trigger.SCHEDULED)
    tasks.run_scan_job.delay(job.id)
    return job


def enqueue_scan(competitor, *, trigger=ScanJob.Trigger.MANUAL):
    """Create a queued ScanJob and dispatch it to the scraping queue.

    Skips creating a duplicate if the competitor already has an active job.
    Returns the ScanJob (existing active one, or the newly created).
    """
    from . import tasks

    active = ScanJob.objects.filter(
        competitor=competitor, status__in=[ScanJob.Status.QUEUED, ScanJob.Status.RUNNING]
    ).first()
    if active is not None:
        return active
    job = create_scan_job(competitor, trigger=trigger)
    tasks.run_scan_job.delay(job.id)
    return job


def execute_scan_job(job_id):
    """Run one ScanJob. The real scraping pipeline is added in the next commit;
    for now this records a clean run and advances the competitor's scan clock."""
    job = ScanJob.objects.select_related("competitor", "workspace").filter(id=job_id).first()
    if job is None or job.status not in (ScanJob.Status.QUEUED, ScanJob.Status.RUNNING):
        return None

    now = timezone.now()
    job.status = ScanJob.Status.RUNNING
    job.started_at = now
    job.save(update_fields=["status", "started_at"])

    competitor = job.competitor
    try:
        # --- pipeline goes here (next commit) ---
        summary = {"products_found": 0, "products_updated": 0, "changes_detected": 0, "pages_requested": 0}
        job.products_found = summary["products_found"]
        job.products_updated = summary["products_updated"]
        job.changes_detected = summary["changes_detected"]
        job.pages_requested = summary["pages_requested"]
        job.status = ScanJob.Status.COMPLETED
    except Exception as exc:  # pragma: no cover - defensive; real handling next commit
        job.status = ScanJob.Status.FAILED
        job.errors_count += 1
        job.error_summary = str(exc)[:2000]
    finally:
        job.finished_at = timezone.now()
        job.save()
        Competitor.objects.filter(id=competitor.id).update(
            last_scan_at=job.finished_at,
            next_scan_at=next_scan_time(competitor, job.finished_at),
            status=Competitor.Status.HEALTHY
            if job.status == ScanJob.Status.COMPLETED and competitor.status == Competitor.Status.SCANNING
            else competitor.status,
        )
        release_scan_lock(competitor.id)
    return job
