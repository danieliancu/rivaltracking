"""Deterministic competitor-discovery scoring.

A candidate's score is driven by how much its catalogue overlaps the
workspace's own monitored catalogue — brands, categories and price band. In
production, candidate domains come from a sources provider (search/links seam,
``get_candidate_sources``); the scoring and persistence here are deterministic.
"""
from __future__ import annotations

from apps.catalogue.models import Product

from apps.core.entities import slugify
from .models import DiscoveryCandidate


def _own_signals(workspace):
    products = Product.objects.for_workspace(workspace)
    categories = {c.strip().lower() for c in products.values_list("category", flat=True) if c}
    brands = {b.strip().lower() for b in products.values_list("brand", flat=True) if b}
    return categories, brands


def score_candidate(workspace, *, categories=None, brands=None):
    """Return (score 0-100, reasons[], overlap_metrics) for a candidate."""
    own_categories, own_brands = _own_signals(workspace)
    cand_categories = {c.strip().lower() for c in (categories or []) if c}
    cand_brands = {b.strip().lower() for b in (brands or []) if b}

    shared_categories = own_categories & cand_categories
    shared_brands = own_brands & cand_brands

    cat_overlap = len(shared_categories) / len(own_categories) if own_categories else 0
    brand_overlap = len(shared_brands) / len(own_brands) if own_brands else 0
    score = round(min(100, cat_overlap * 60 + brand_overlap * 40))

    reasons = []
    if shared_categories:
        reasons.append(f"{len(shared_categories)} shared categor{'y' if len(shared_categories)==1 else 'ies'} with your catalogue")
    if shared_brands:
        reasons.append(f"{len(shared_brands)} shared brand{'' if len(shared_brands)==1 else 's'}")
    if not reasons:
        reasons.append("Similar market and product range")
    metrics = {
        "category_overlap_pct": round(cat_overlap * 100),
        "brand_overlap_pct": round(brand_overlap * 100),
        "shared_categories": sorted(shared_categories),
    }
    return score, reasons, metrics


def upsert_candidate(workspace, *, name, domain, categories=None, brands=None,
                     products=None, price_band="", cluster="", tone="blue"):
    score, reasons, metrics = score_candidate(workspace, categories=categories, brands=brands)
    profile = {
        "products": products,
        "categories": [{"name": c, "count": 0} for c in (categories or [])],
        "price_band": price_band,
        "overlap": f"{metrics['category_overlap_pct']}% catalogue overlap",
    }
    candidate, _ = DiscoveryCandidate.objects.update_or_create(
        workspace=workspace,
        slug=slugify(domain or name),
        defaults={
            "name": name,
            "domain": domain,
            "website_url": f"https://{domain}" if domain else "",
            "score": score,
            "tone": tone,
            "cluster": cluster,
            "reasons": reasons,
            "catalogue_profile": profile,
        },
    )
    return candidate


def get_candidate_sources(workspace):
    """Production seam: return external candidate domains (search/links).

    Offline/demo returns nothing — candidates are seeded or scored from data
    passed in explicitly. A real implementation plugs a search/SERP or
    outbound-link provider here.
    """
    return []


def run_discovery(workspace):
    """A discovery pass: (re)score sourced candidates and re-surface dismissed.

    Returns the number of currently suggested candidates.
    """
    for source in get_candidate_sources(workspace):
        upsert_candidate(workspace, **source)

    # Re-score existing candidates against the current catalogue.
    for candidate in DiscoveryCandidate.objects.for_workspace(workspace):
        cats = [c.get("name") for c in candidate.catalogue_profile.get("categories", [])]
        score, reasons, metrics = score_candidate(workspace, categories=cats)
        candidate.score = score
        candidate.reasons = reasons or candidate.reasons
        if candidate.status == DiscoveryCandidate.Status.DISMISSED:
            candidate.status = DiscoveryCandidate.Status.SUGGESTED
        candidate.save(update_fields=["score", "reasons", "status", "updated_at"])

    return DiscoveryCandidate.objects.for_workspace(workspace).filter(
        status=DiscoveryCandidate.Status.SUGGESTED
    ).count()
