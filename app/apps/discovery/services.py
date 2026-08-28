"""Discovery mutations against the mock store."""
from apps.core.mock.store import MockStore


def monitor_candidate(request, slug):
    """Future: POST /api/discovery/:id/monitor

    Flips the candidate to monitoring and registers it as an initialising
    competitor with its discovered catalogue size (workspace-store.tsx).
    """
    store = MockStore(request)
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

    from apps.competitors.services import _row_from_url

    row = _row_from_url(candidate["url"])
    row.update(
        {
            "slug": candidate["slug"],
            "name": candidate["name"],
            "url": candidate["url"],
            "products": candidate["catalogue_profile"]["products"],
        }
    )

    def _add(rows):
        if not any(c["slug"] == row["slug"] for c in rows):
            rows.append(row)

    store.mutate("competitors", _add)
    return candidate


def dismiss_candidate(request, slug):
    """Future: POST /api/discovery/:id/dismiss"""

    def _dismiss(candidates):
        for c in candidates:
            if c["slug"] == slug:
                c["status"] = "dismissed"

    MockStore(request).mutate("discovery_candidates", _dismiss)


def mark_not_relevant(request, slug):
    """Future: POST /api/discovery/:id/feedback — removes the candidate."""
    store = MockStore(request)
    store.replace(
        "discovery_candidates",
        [c for c in store.get("discovery_candidates") if c["slug"] != slug],
    )


def run_discovery(request):
    """Future: POST /api/discovery/run

    The mock restores previously dismissed candidates to "suggested" and
    reports how many suggestions were refreshed (workspace-store.tsx).
    """
    store = MockStore(request)
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
