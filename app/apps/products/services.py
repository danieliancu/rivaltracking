"""Product mutations over the mock store (port of services/products.ts)."""
from apps.core.mock.store import MockStore


def toggle_watchlist(request, slug):
    """Future: POST /api/watchlist · DELETE /api/watchlist/:slug.

    Returns True when the product was added, False when removed.
    """

    def fn(watchlist):
        if slug in watchlist:
            watchlist.remove(slug)
            return False
        watchlist.append(slug)
        return True

    return MockStore(request).mutate("watchlist", fn)


def add_to_watchlist(request, slugs):
    """Future: POST /api/watchlist (bulk). Returns how many were newly added."""

    def fn(watchlist):
        fresh = [s for s in slugs if s not in watchlist]
        watchlist.extend(fresh)
        return len(fresh)

    return MockStore(request).mutate("watchlist", fn)
