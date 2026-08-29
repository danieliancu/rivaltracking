"""Competitor mutations against the ORM (workspace-scoped).

Each function notes the future backend endpoint it stands in for. Scanning
itself is Phase 3; run_scan remains a deterministic placeholder that just
stamps the row as freshly scanned.
"""
import re

from apps.core.entities import competitor_tone, slugify

from . import selectors
from .models import Competitor

DEFAULT_CONFIG = {
    "frequency": "Every 24 hours",
    "track_prices": True,
    "track_stock": True,
    "track_products": True,
    "track_promotions": True,
}


def _fields_from_url(url):
    """Port of services/competitors.ts addCompetitor(): derive display name +
    slug + domain from the host."""
    host = re.sub(r"^https?://", "", url.strip())
    host = re.sub(r"^www\.", "", host)
    host = re.sub(r"/.*$", "", host)
    stem = host.split(".")[0]
    stem = re.sub(r"[-_]", " ", stem).title().replace(" ", "")
    name = stem + (host[host.index(".") :] if "." in host else "")
    return {"slug": slugify(host), "name": name, "domain": host}


def _workspace(request):
    return getattr(request, "workspace", None)


def add_competitor(request, url):
    """Create a competitor from a URL and queue its first real scan.

    No fabricated headline metrics: products_count/market stay empty until a
    scan populates them (locally, without SCANNING_LIVE, that means 0 products).
    """
    from apps.scanning.models import ScanJob
    from apps.scanning.services import enqueue_scan

    workspace = _workspace(request)
    fields = _fields_from_url(url)
    competitor, created = Competitor.objects.get_or_create(
        workspace=workspace,
        slug=fields["slug"],
        defaults={
            "name": fields["name"],
            "domain": fields["domain"],
            "website_url": f"https://{fields['domain']}",
            "status": Competitor.Status.INITIALISING,
            "monitoring_enabled": True,
            "tone": competitor_tone(fields["name"]),
        },
    )
    if created:
        enqueue_scan(competitor, trigger=ScanJob.Trigger.INITIAL)
        competitor.refresh_from_db()
    return selectors.row_dict(competitor)


def run_scan(request, slug):
    """Create a real ScanJob and enqueue it (POST /api/competitors/:id/scan).

    In eager mode (local/tests) the job runs inline, so the returned summary is
    final; with real workers it returns the queued job and the UI reflects
    progress via ScanJob.
    """
    from apps.scanning.models import ScanJob
    from apps.scanning.services import enqueue_scan

    competitor = Competitor.objects.for_workspace(_workspace(request)).filter(slug=slug).first()
    if competitor is None:
        return None
    job = enqueue_scan(competitor, trigger=ScanJob.Trigger.MANUAL)
    job.refresh_from_db()
    return {
        "new_changes": job.changes_detected,
        "status": job.status,
        "job_id": job.id,
    }


def set_status(request, slug, status):
    """Future: PATCH /api/competitors/:id (pause/resume)"""
    enabled = status != Competitor.Status.PAUSED
    Competitor.objects.for_workspace(_workspace(request)).filter(slug=slug).update(
        status=status, monitoring_enabled=enabled
    )


def remove_competitor(request, slug):
    """Future: DELETE /api/competitors/:id"""
    Competitor.objects.for_workspace(_workspace(request)).filter(slug=slug).delete()


def save_monitoring_config(request, slug, config):
    """Future: PUT /api/competitors/:id/monitoring-config"""
    Competitor.objects.for_workspace(_workspace(request)).filter(slug=slug).update(
        monitoring_frequency=config.get("frequency", DEFAULT_CONFIG["frequency"]),
        track_prices=config.get("track_prices", True),
        track_stock=config.get("track_stock", True),
        track_products=config.get("track_products", True),
        track_promotions=config.get("track_promotions", True),
    )


def get_monitoring_config(request, slug):
    c = Competitor.objects.for_workspace(_workspace(request)).filter(slug=slug).first()
    if c is None:
        return dict(DEFAULT_CONFIG)
    return {
        "frequency": c.monitoring_frequency,
        "track_prices": c.track_prices,
        "track_stock": c.track_stock,
        "track_products": c.track_products,
        "track_promotions": c.track_promotions,
    }
