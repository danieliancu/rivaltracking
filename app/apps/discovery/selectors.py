"""Discovery reads over the DiscoveryCandidate model.

candidate_dict rebuilds the Phase 1 candidate dict the templates consume so the
Discovery UI is unchanged.
"""
from .data import DISCOVERY_CLUSTERS
from .models import DiscoveryCandidate

DISCOVERY_TONES = {
    "blue": "bg-info/10 text-info",
    "purple": "bg-purple/10 text-purple",
    "teal": "bg-teal/10 text-teal",
    "orange": "bg-warning/10 text-warning",
}

def reference_profile(request):
    """Derived 'your catalogue' reference for the compare drawer (real data)."""
    from apps.catalogue.models import Product, ProductListing

    ws = getattr(request, "workspace", None)
    products = Product.objects.for_workspace(ws).count()
    cats = list(
        Product.objects.for_workspace(ws).exclude(category="")
        .values_list("category", flat=True).distinct()[:3]
    )
    prices = list(
        ProductListing.objects.for_workspace(ws).exclude(current_price=None)
        .values_list("current_price", flat=True)
    )
    band = f"£{min(prices):.0f} – £{max(prices):.0f}" if prices else "—"
    return {
        "name": "Your catalogue",
        "products": f"{products:,}",
        "price_band": band,
        "categories": " · ".join(cats) or "—",
    }


def _workspace(request):
    return getattr(request, "workspace", None)


def candidate_dict(obj):
    return {
        "id": obj.slug,
        "slug": obj.slug,
        "name": obj.name,
        "url": obj.domain or obj.website_url,
        "match": obj.score,
        "tone": obj.tone or "blue",
        "cluster": obj.cluster,
        "status": obj.status,
        "why_match": obj.reasons or [],
        "catalogue_profile": obj.catalogue_profile or {},
    }


def _queryset(request):
    return DiscoveryCandidate.objects.for_workspace(_workspace(request))


def visible_candidates(request, cluster=None, limit=None):
    qs = _queryset(request).exclude(status=DiscoveryCandidate.Status.DISMISSED)
    if cluster:
        qs = qs.filter(cluster=cluster)
    rows = [candidate_dict(c) for c in (qs[:limit] if limit else qs)]
    return rows


def by_slug(request, slug):
    obj = _queryset(request).filter(slug=slug).first()
    return candidate_dict(obj) if obj else None


def tone_class(candidate):
    return DISCOVERY_TONES.get(candidate.get("tone"), DISCOVERY_TONES["blue"])


def cluster_cards(request, active_cluster=None):
    candidates = _queryset(request).exclude(status=DiscoveryCandidate.Status.DISMISSED)
    counts = {}
    for cl in candidates.values_list("cluster", flat=True):
        counts[cl] = counts.get(cl, 0) + 1
    return [
        {
            "id": c["id"],
            "label": c["label"],
            "count": counts.get(c["id"], 0),
            "active": active_cluster == c["id"],
        }
        for c in DISCOVERY_CLUSTERS
    ]
