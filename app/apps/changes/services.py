"""Changes-page mutations over the ORM (shared workspace watchlist)."""
from apps.products.services import add_to_watchlist as _add_to_watchlist


def add_to_watchlist(request, slugs):
    """Add product slugs to the shared watchlist; returns how many were new.

    Delegates to the products service so both pages share one implementation.
    Future: POST /api/watchlist/items
    """
    return _add_to_watchlist(request, slugs)
