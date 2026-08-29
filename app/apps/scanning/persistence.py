"""Turn scraped items into ProductListings, history and ChangeEvents.

This is the ``persist_hook`` the orchestrator calls. On a competitor's first
completed scan it establishes a baseline (listings + initial snapshots, no
change events); afterwards it detects and records real changes. Disappeared
listings are only marked removed after repeated misses.
"""
from __future__ import annotations

from django.conf import settings
from django.utils import timezone

from apps.catalogue import services as catalogue_services
from apps.catalogue.models import Product, ProductListing
from apps.changes import detection
from apps.core.entities import competitor_tone, slugify

from .models import ScanJob


def _unique_product_slug(workspace, title):
    base = slugify(title) or "product"
    slug = base
    i = 2
    while Product.objects.filter(workspace=workspace, slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


def _listing_for(competitor, normalized):
    """Find an existing listing for this normalised item (source_url, then SKU)."""
    ws = competitor.workspace
    if normalized.source_url:
        listing = ProductListing.objects.filter(
            workspace=ws, competitor=competitor, source_url=normalized.source_url
        ).select_related("product").first()
        if listing:
            return listing
    if normalized.sku:
        return (
            ProductListing.objects.filter(
                workspace=ws, competitor=competitor, competitor_sku=normalized.sku
            )
            .select_related("product")
            .first()
        )
    return None


def upsert_listing(competitor, normalized, *, now):
    """Create or update the ProductListing; return (listing, created, previous)."""
    ws = competitor.workspace
    listing = _listing_for(competitor, normalized)

    if listing is None:
        product = Product.objects.create(
            workspace=ws,
            name=normalized.title,
            slug=_unique_product_slug(ws, normalized.title),
            brand=normalized.brand,
            sku=normalized.sku,
            gtin=normalized.gtin,
            ean=normalized.ean,
            upc=normalized.upc,
            mpn=normalized.mpn,
            category=normalized.category,
            image_url=normalized.image_url,
            tone=competitor_tone(normalized.title or competitor.name),
            icon="package",
        )
        listing = ProductListing.objects.create(
            workspace=ws,
            product=product,
            competitor=competitor,
            source_url=normalized.source_url,
            competitor_sku=normalized.sku,
            competitor_product_name=normalized.title,
            current_price=normalized.price,
            currency=normalized.currency,
            current_stock_status=normalized.stock_status,
            current_promotion=normalized.promotion,
            is_primary=True,
            first_seen_at=now,
            last_seen_at=now,
            last_change_at=now,
        )
        return listing, True, None

    previous = {
        "price": listing.current_price,
        "stock": listing.current_stock_status,
        "promotion": listing.current_promotion or "",
        "title": listing.competitor_product_name,
        "category": listing.product.category if listing.product else "",
    }
    if normalized.price is not None and normalized.price != listing.current_price:
        listing.previous_price = listing.current_price
    listing.current_price = normalized.price if normalized.price is not None else listing.current_price
    listing.current_stock_status = normalized.stock_status
    listing.current_promotion = normalized.promotion
    listing.currency = normalized.currency
    listing.competitor_product_name = normalized.title or listing.competitor_product_name
    listing.last_seen_at = now
    listing.consecutive_misses = 0
    listing.save()
    return listing, False, previous


def _is_baseline(competitor, job):
    prior = ScanJob.objects.filter(
        competitor=competitor, status=ScanJob.Status.COMPLETED
    )
    if job is not None:
        prior = prior.exclude(id=job.id)
    return not prior.exists()


def persist_scan(competitor, items, job=None):
    """persist_hook: upsert listings, write history, detect changes, handle misses."""
    from apps.changes.significance import is_ai_eligible

    now = timezone.now()
    baseline = _is_baseline(competitor, job)
    seen_ids = set()
    changes = 0
    updated = 0
    ai_eligible = []

    for item in items:
        listing, created, previous = upsert_listing(competitor, item.normalized, now=now)
        seen_ids.add(listing.id)
        catalogue_services.record_snapshots(listing, now=now)
        if not created:
            updated += 1
        if baseline:
            continue
        events = detection.detect_for_listing(
            listing, previous, detected_at=now, is_new=created
        )
        if events:
            first = events[0]
            listing.change_kind = first.kind
            listing.change_label = first.label
            listing.last_change_at = now
            listing.save(update_fields=["change_kind", "change_label", "last_change_at"])
        changes += len(events)
        ai_eligible.extend(e for e in events if e and is_ai_eligible(e))

    if not baseline and items:
        changes += _handle_disappearances(competitor, seen_ids, now)

    _enqueue_ai_analyses(ai_eligible)

    if job is not None:
        job.changes_detected = (job.changes_detected or 0) + changes
        job.products_updated = (job.products_updated or 0) + updated
    return {"changes": changes, "updated": updated}


def _enqueue_ai_analyses(events):
    """Funnel: only significant events get an (expensive) AI analysis, capped."""
    if not events:
        return
    from apps.ai.tasks import analyse_change

    for event in events[: settings.AI_MAX_ANALYSES_PER_SCAN]:
        analyse_change.delay(event.id)


def _handle_disappearances(competitor, seen_ids, now):
    threshold = settings.LISTING_MISSES_BEFORE_REMOVED
    missing = ProductListing.objects.filter(
        workspace=competitor.workspace, competitor=competitor, active=True
    ).exclude(id__in=seen_ids)
    removed = 0
    for listing in missing:
        listing.consecutive_misses += 1
        if listing.consecutive_misses >= threshold:
            listing.active = False
            listing.save(update_fields=["consecutive_misses", "active"])
            removed += len(detection.record_removed(listing, detected_at=now))
        else:
            listing.save(update_fields=["consecutive_misses"])
    return removed
