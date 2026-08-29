"""Scan orchestration services (framework only in this commit; the real
fetch/extract/normalise/persist pipeline is wired in the next commit)."""
from datetime import timedelta

from django.conf import settings
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


def execute_scan_job(job_id, *, fetcher=None, persist_hook=None):
    """Run one ScanJob through the scraping orchestrator.

    Live scanning (settings.SCANNING_LIVE) hits real sites; tests inject a fake
    ``fetcher`` to drive the pipeline offline. With neither, this records a clean
    no-op run (so eager local Run Scan never touches the network).
    ``persist_hook`` turns scraped items into listings/snapshots/changes
    (wired in the next commit).
    """
    job = ScanJob.objects.select_related("competitor", "workspace").filter(id=job_id).first()
    if job is None or job.status not in (ScanJob.Status.QUEUED, ScanJob.Status.RUNNING):
        return None

    now = timezone.now()
    job.status = ScanJob.Status.RUNNING
    job.started_at = now
    job.save(update_fields=["status", "started_at"])

    competitor = job.competitor
    try:
        if fetcher is not None or settings.SCANNING_LIVE:
            from .persistence import persist_scan
            from .scraping.orchestration import run_competitor_scan

            outcome = run_competitor_scan(
                competitor,
                fetcher=fetcher,
                job=job,
                throttle=fetcher is None,
                persist_hook=persist_hook or persist_scan,
            )
            job.products_found = outcome.products_found
            job.pages_requested = outcome.pages_requested
            job.errors_count = outcome.errors
            job.error_summary = "\n".join(outcome.error_messages[:20])
            job.status = (
                ScanJob.Status.PARTIALLY_FAILED
                if outcome.errors and outcome.products_found
                else ScanJob.Status.FAILED
                if outcome.errors and not outcome.products_found
                else ScanJob.Status.COMPLETED
            )
        else:
            job.status = ScanJob.Status.COMPLETED
    except Exception as exc:  # defensive: a scan failure never breaks other work
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
