"""Changes-page mutations over the mock store."""
from apps.core.mock.store import MockStore


def add_to_watchlist(request, slugs):
    """Add product slugs to the shared watchlist; returns how many were new.

    Future: POST /api/watchlist/items
    """
    store = MockStore(request)
    current = store.get("watchlist")
    new_slugs = [s for s in slugs if s not in current]
    if new_slugs:
        store.mutate("watchlist", lambda rows: rows.extend(new_slugs))
    return len(new_slugs)
