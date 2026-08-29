"""Deterministic product matching (identifiers first, AI never).

Hierarchy (high-confidence deterministic first):
  1. GTIN/EAN/UPC   → 99
  2. MPN + brand    → 95
  3. exact SKU      → 90
  4. brand + title token similarity (rapidfuzz)
  5. title similarity (rapidfuzz)
Auto-apply at/above AUTO_THRESHOLD (repoint the listing to the shared canonical
product and merge away the orphan); REVIEW_THRESHOLD..AUTO stays reviewable.
"""
from __future__ import annotations

from rapidfuzz import fuzz

from apps.catalogue.models import Product, ProductListing

from .models import MatchResult

AUTO_THRESHOLD = 90.0
REVIEW_THRESHOLD = 70.0


def _candidates(listing):
    """Other products in the workspace (not this listing's own product)."""
    return Product.objects.for_workspace(listing.workspace).exclude(
        id=listing.product_id
    )


def _best_deterministic(listing):
    product = listing.product
    ws = listing.workspace
    others = _candidates(listing)

    if product and product.gtin:
        hit = others.filter(gtin=product.gtin).first()
        if hit:
            return hit, 99.0, MatchResult.Method.GTIN
    if product and product.mpn and product.brand:
        hit = others.filter(mpn=product.mpn, brand__iexact=product.brand).first()
        if hit:
            return hit, 95.0, MatchResult.Method.MPN
    if product and product.sku:
        hit = others.filter(sku__iexact=product.sku).first()
        if hit:
            return hit, 90.0, MatchResult.Method.SKU
    return None, 0.0, MatchResult.Method.NONE


def _best_fuzzy(listing):
    product = listing.product
    title = (product.name if product else listing.competitor_product_name) or ""
    if not title:
        return None, 0.0, MatchResult.Method.NONE
    best, best_score = None, 0.0
    for candidate in _candidates(listing).only("id", "name", "brand"):
        score = fuzz.token_sort_ratio(title, candidate.name)
        if product and product.brand and candidate.brand:
            if product.brand.lower() == candidate.brand.lower():
                score = min(100.0, score + 5)
        if score > best_score:
            best, best_score = candidate, score
    method = MatchResult.Method.TITLE
    return best, float(best_score), method


def match_listing(listing):
    """Compute and persist the MatchResult for one listing; auto-merge if strong."""
    hit, confidence, method = _best_deterministic(listing)
    if hit is None:
        hit, confidence, method = _best_fuzzy(listing)

    if hit is None or confidence < REVIEW_THRESHOLD:
        return _save(listing, listing.product, 0.0, MatchResult.Method.NONE, MatchResult.Status.UNMATCHED)

    if confidence >= AUTO_THRESHOLD:
        _merge_into(listing, hit)
        return _save(listing, hit, confidence, method, MatchResult.Status.AUTO_MATCHED)

    return _save(listing, hit, confidence, method, MatchResult.Status.REVIEW_REQUIRED)


def _merge_into(listing, canonical):
    """Repoint the listing to the shared canonical product; drop the orphan."""
    orphan = listing.product
    if orphan and orphan.id != canonical.id:
        listing.product = canonical
        listing.is_primary = False
        listing.save(update_fields=["product", "is_primary"])
        if not ProductListing.objects.filter(product=orphan).exists():
            # Carry over match metadata for the compare drawer, then delete.
            if orphan.match_confidence and not canonical.match_confidence:
                canonical.match_confidence = orphan.match_confidence
                canonical.save(update_fields=["match_confidence"])
            orphan.delete()
    # Ensure the canonical has a primary listing and a confidence for the UI.
    if not canonical.listings.filter(is_primary=True).exists():
        first = canonical.listings.order_by("id").first()
        if first:
            canonical.listings.filter(id=first.id).update(is_primary=True)


def _save(listing, product, confidence, method, status):
    result, _ = MatchResult.objects.update_or_create(
        listing=listing,
        defaults={
            "workspace": listing.workspace,
            "product": product,
            "confidence": confidence,
            "method": method,
            "status": status,
        },
    )
    if status == MatchResult.Status.AUTO_MATCHED and product is not None:
        best = max(confidence, product.match_confidence or 0)
        Product.objects.filter(id=product.id).update(match_confidence=int(best))
    return result


def match_competitor(competitor):
    """Match every active listing for a competitor (called after a scan)."""
    count = 0
    for listing in ProductListing.objects.for_workspace(competitor.workspace).filter(
        competitor=competitor, active=True
    ).select_related("product"):
        match_listing(listing)
        count += 1
    return count
