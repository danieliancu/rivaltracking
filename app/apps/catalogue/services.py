"""Change-aware history writes for listings + own-catalogue connection helpers.

Snapshots are only written when the value actually changed (or no snapshot
exists yet), so identical values on every scan don't create meaningless rows
while charts still get every real movement.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.utils import timezone

from .models import PriceSnapshot, Promotion, StockSnapshot


def record_price_snapshot(listing, *, now=None):
    if listing.current_price is None:
        return None
    now = now or timezone.now()
    last = (
        listing.price_snapshots.order_by("-captured_at")
        .values_list("price", flat=True)
        .first()
    )
    if last is not None and last == listing.current_price:
        return None
    return PriceSnapshot.objects.create(
        workspace=listing.workspace,
        listing=listing,
        price=listing.current_price,
        currency=listing.currency,
        captured_at=now,
    )


def record_stock_snapshot(listing, *, now=None):
    now = now or timezone.now()
    last = (
        listing.stock_snapshots.order_by("-captured_at")
        .values_list("stock_status", flat=True)
        .first()
    )
    if last == listing.current_stock_status:
        return None
    return StockSnapshot.objects.create(
        workspace=listing.workspace,
        listing=listing,
        stock_status=listing.current_stock_status,
        quantity=listing.current_stock_quantity,
        captured_at=now,
    )


def sync_promotion(listing, *, now=None):
    """Open a Promotion row when one starts; close the active one when it ends."""
    now = now or timezone.now()
    active = listing.promotions.filter(active=True).order_by("-captured_at").first()
    current = listing.current_promotion or ""
    if current and (active is None or active.title != current):
        if active is not None:
            active.active = False
            active.ended_at = now
            active.save(update_fields=["active", "ended_at"])
        return Promotion.objects.create(
            workspace=listing.workspace,
            listing=listing,
            title=current,
            promotion_type="detected",
            value=current,
            started_at=now,
            active=True,
            captured_at=now,
        )
    if not current and active is not None:
        active.active = False
        active.ended_at = now
        active.save(update_fields=["active", "ended_at"])
    return None


def record_snapshots(listing, *, now=None):
    now = now or timezone.now()
    record_price_snapshot(listing, now=now)
    record_stock_snapshot(listing, now=now)
    sync_promotion(listing, now=now)


def unique_product_slug(workspace, name):
    """A canonical-product slug unique within a workspace."""
    from apps.core.entities import slugify

    from .models import Product

    base = slugify(name) or "product"
    slug = base
    i = 2
    while Product.objects.filter(workspace=workspace, slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


# ---------------------------------------------------------------------------
# Own-catalogue connection (website source)

def _domain_from_url(url):
    from urllib.parse import urlparse
    import re

    host = urlparse(url if "://" in url else f"https://{url}").netloc or url
    return re.sub(r"^www\.", "", host).strip("/").lower()


def get_source(workspace, source_type="website"):
    from .models import OwnCatalogueSource

    return OwnCatalogueSource.objects.for_workspace(workspace).filter(
        source_type=source_type
    ).first()


def connect_website(workspace, url):
    """Create/update the website source and enqueue an import. Returns source."""
    from .models import OwnCatalogueSource
    from . import tasks

    url = url.strip()
    if not url:
        return None, "Enter your store's website address."
    if "://" not in url:
        url = f"https://{url}"
    domain = _domain_from_url(url)
    if not domain or "." not in domain:
        return None, "Enter a valid website address, e.g. mystore.co.uk."
    source, _ = OwnCatalogueSource.objects.update_or_create(
        workspace=workspace,
        source_type=OwnCatalogueSource.SourceType.WEBSITE,
        defaults={
            "website_url": url,
            "domain": domain,
            "status": OwnCatalogueSource.Status.IMPORTING,
        },
    )
    tasks.import_catalogue.delay(source.id)
    source.refresh_from_db()
    return source, None


def rescan_website(workspace):
    from . import tasks

    source = get_source(workspace, "website")
    if source is None:
        return None
    tasks.import_catalogue.delay(source.id)
    source.refresh_from_db()
    return source


def disconnect_source(workspace, source_type="website"):
    """Remove a catalogue source and the own products it imported."""
    from .models import OwnProduct

    source = get_source(workspace, source_type)
    if source is None:
        return
    OwnProduct.objects.filter(workspace=workspace, source=source).delete()
    source.delete()


def upsert_own_product_dict(workspace, data, *, source=None):
    """Upsert one OwnProduct from a plain dict (API/CSV shared path) + match."""
    from apps.core.entities import slugify
    from apps.matching.engine import match_own_product

    from .models import OwnListing, OwnProduct

    sku = (str(data.get("sku") or "").strip() or slugify(str(data.get("name") or "")))[:80]
    if not sku:
        return None, "missing sku/name"
    price = data.get("price")
    try:
        price = None if price in (None, "") else Decimal(str(price))
    except (InvalidOperation, TypeError):
        price = None
    own, created = OwnProduct.objects.update_or_create(
        workspace=workspace,
        own_sku=sku,
        defaults={
            "name": (str(data.get("name") or sku))[:200],
            "brand": (str(data.get("brand") or ""))[:120],
            "gtin": (str(data.get("gtin") or ""))[:14],
            "ean": (str(data.get("ean") or ""))[:14],
            "mpn": (str(data.get("mpn") or ""))[:80],
            "category": (str(data.get("category") or ""))[:120],
            "our_price": price,
            "currency": (str(data.get("currency") or "GBP"))[:3].upper(),
            "source": source,
        },
    )
    url = str(data.get("url") or "").strip()
    if url:
        OwnListing.objects.update_or_create(
            workspace=workspace, own_product=own, channel="api",
            defaults={"url": url[:500], "price": own.our_price, "currency": own.currency},
        )
    match_own_product(own)
    return own, None if created else "updated"


def ensure_api_token(workspace):
    import secrets

    s = workspace.settings
    if not s.api_token:
        s.api_token = secrets.token_urlsafe(32)
        s.save(update_fields=["api_token", "updated_at"])
    return s.api_token
