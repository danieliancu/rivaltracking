"""Scan orchestration services (framework only in this commit; the real
fetch/extract/normalise/persist pipeline is wired in the next commit)."""
import logging
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.competitors.models import Competitor

from .models import ScanJob

logger = logging.getLogger("rivaltracking.scanning")

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


def _dispatch_scan_job(job):
    """Send a ScanJob to a worker, or run it off-thread for local live scans.

    Under a real broker the worker owns it. In eager mode a live scan would
    otherwise block the web request for the whole crawl, so when both eager and
    SCANNING_LIVE are on we run it in a background thread and mark the competitor
    ``scanning`` immediately (the table/detail then reflect progress). Eager +
    non-live (tests, offline dev) stays inline so results are ready on return.
    """
    from . import tasks

    if settings.CELERY_TASK_ALWAYS_EAGER and settings.SCANNING_LIVE:
        import threading

        from django.db import connection

        Competitor.objects.filter(id=job.competitor_id).update(
            status=Competitor.Status.SCANNING
        )

        def _run():
            try:
                execute_scan_job(job.id)
            finally:
                connection.close()  # each thread owns its DB connection

        threading.Thread(target=_run, daemon=True).start()
    else:
        tasks.run_scan_job.delay(job.id)


def enqueue_scan(competitor, *, trigger=ScanJob.Trigger.MANUAL):
    """Create a queued ScanJob and dispatch it to the scraping queue.

    Skips creating a duplicate if the competitor already has an active job.
    Returns the ScanJob (existing active one, or the newly created).
    """
    active = ScanJob.objects.filter(
        competitor=competitor, status__in=[ScanJob.Status.QUEUED, ScanJob.Status.RUNNING]
    ).first()
    if active is not None:
        return active
    job = create_scan_job(competitor, trigger=trigger)
    _dispatch_scan_job(job)
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
    logger.info(
        "scan.started job=%s workspace=%s competitor=%s trigger=%s",
        job.id, job.workspace_id, competitor.slug, job.trigger_type,
    )
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
            if outcome.products_found and job.status != ScanJob.Status.FAILED:
                from apps.matching.tasks import match_competitor_listings

                match_competitor_listings.delay(competitor.id)
        else:
            job.status = ScanJob.Status.COMPLETED
    except Exception as exc:  # defensive: a scan failure never breaks other work
        job.status = ScanJob.Status.FAILED
        job.errors_count += 1
        job.error_summary = str(exc)[:2000]
    finally:
        job.finished_at = timezone.now()
        job.save()
        logger.info(
            "scan.finished job=%s status=%s pages=%s products=%s changes=%s errors=%s",
            job.id, job.status, job.pages_requested, job.products_found,
            job.changes_detected, job.errors_count,
        )
        from apps.catalogue.models import ProductListing

        product_count = ProductListing.objects.filter(
            competitor_id=competitor.id, active=True
        ).count()
        settled = job.status in (
            ScanJob.Status.COMPLETED,
            ScanJob.Status.PARTIALLY_FAILED,
        )
        pre_active = competitor.status in (
            Competitor.Status.SCANNING,
            Competitor.Status.INITIALISING,
        )
        Competitor.objects.filter(id=competitor.id).update(
            last_scan_at=job.finished_at,
            next_scan_at=next_scan_time(competitor, job.finished_at),
            products_count=product_count,
            status=Competitor.Status.HEALTHY
            if settled and pre_active
            else competitor.status,
        )
        release_scan_lock(competitor.id)
    return job
