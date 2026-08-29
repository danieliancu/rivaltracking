"""Product mutations over the ORM (workspace-scoped watchlist)."""
from apps.catalogue.models import Product

from .models import WatchlistItem


def _workspace(request):
    return getattr(request, "workspace", None)


def _user(request):
    user = getattr(request, "user", None)
    return user if (user is not None and user.is_authenticated) else None


def toggle_watchlist(request, slug):
    """Future: POST /api/watchlist · DELETE /api/watchlist/:slug.

    Returns True when the product was added, False when removed.
    """
    workspace = _workspace(request)
    product = Product.objects.for_workspace(workspace).filter(slug=slug).first()
    if product is None:
        return False
    existing = WatchlistItem.objects.filter(workspace=workspace, product=product).first()
    if existing:
        existing.delete()
        return False
    WatchlistItem.objects.create(
        workspace=workspace, product=product, added_by=_user(request)
    )
    return True


def add_to_watchlist(request, slugs):
    """Future: POST /api/watchlist (bulk). Returns how many were newly added."""
    workspace = _workspace(request)
    products = Product.objects.for_workspace(workspace).filter(slug__in=slugs)
    already = set(
        WatchlistItem.objects.filter(
            workspace=workspace, product__in=products
        ).values_list("product_id", flat=True)
    )
    user = _user(request)
    created = [
        WatchlistItem(workspace=workspace, product=p, added_by=user)
        for p in products
        if p.id not in already
    ]
    WatchlistItem.objects.bulk_create(created)
    return len(created)
