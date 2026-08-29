"""Discovery mutations. Candidate state lives in the workspace demo store;
starting monitoring creates a real Competitor row for the workspace."""
from django.utils import timezone

from apps.competitors.models import Competitor
from apps.core.entities import competitor_tone
from apps.core.store import WorkspaceStore


def monitor_candidate(request, slug):
    """Future: POST /api/discovery/:id/monitor

    Flips the candidate to monitoring and registers it as an initialising
    Competitor with its discovered catalogue size.
    """
    store = WorkspaceStore(request)
    candidate = next(
        (c for c in store.get("discovery_candidates") if c["slug"] == slug), None
    )
    if candidate is None:
        return None

    def _mark(candidates):
        for c in candidates:
            if c["slug"] == slug:
                c["status"] = "monitoring"

    store.mutate("discovery_candidates", _mark)

    now = timezone.now()
    Competitor.objects.get_or_create(
        workspace=request.workspace,
        slug=candidate["slug"],
        defaults={
            "name": candidate["name"],
            "domain": candidate["url"],
            "website_url": f"https://{candidate['url']}",
            "market": "UK Toys",
            "status": Competitor.Status.INITIALISING,
            "monitoring_enabled": True,
            "tone": competitor_tone(candidate["name"]),
            "products_count": candidate["catalogue_profile"]["products"],
            "last_scan_at": now,
            "next_scan_at": now + timezone.timedelta(hours=24),
        },
    )
    return candidate


def dismiss_candidate(request, slug):
    """Future: POST /api/discovery/:id/dismiss"""

    def _dismiss(candidates):
        for c in candidates:
            if c["slug"] == slug:
                c["status"] = "dismissed"

    WorkspaceStore(request).mutate("discovery_candidates", _dismiss)


def mark_not_relevant(request, slug):
    """Future: POST /api/discovery/:id/feedback — removes the candidate."""
    store = WorkspaceStore(request)
    store.replace(
        "discovery_candidates",
        [c for c in store.get("discovery_candidates") if c["slug"] != slug],
    )


def run_discovery(request):
    """Future: POST /api/discovery/run

    The mock restores previously dismissed candidates to "suggested" and
    reports how many suggestions were refreshed (workspace-store.tsx).
    """
    store = WorkspaceStore(request)
    restored = 0

    def _restore(candidates):
        nonlocal restored
        for c in candidates:
            if c["status"] == "dismissed":
                c["status"] = "suggested"
                restored += 1

    store.mutate("discovery_candidates", _restore)
    fresh = sum(
        1 for c in store.get("discovery_candidates") if c["status"] == "suggested"
    )
    return fresh
