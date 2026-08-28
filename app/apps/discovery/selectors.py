"""Discovery reads over the mock store."""
from apps.core.mock.store import MockStore

from .data import DISCOVERY_CLUSTERS

# Candidate tone → identity tile classes (company-discovery-row.tsx).
DISCOVERY_TONES = {
    "blue": "bg-info/10 text-info",
    "purple": "bg-purple/10 text-purple",
    "teal": "bg-teal/10 text-teal",
    "orange": "bg-warning/10 text-warning",
}

# Catalogue profile of the monitored reference competitor — hard-coded in
# compare-catalogue-drawer.tsx. Comparison uses current catalogue data only.
TOYWORLD_PROFILE = {
    "name": "ToyWorld.co.uk",
    "products": "2,438",
    "price_band": "£5 – £250",
    "categories": "Outdoor Toys · Construction Toys · Educational Toys",
}


def visible_candidates(request, cluster=None, limit=None):
    rows = [
        c
        for c in MockStore(request).get("discovery_candidates")
        if c["status"] != "dismissed" and (not cluster or c["cluster"] == cluster)
    ]
    return rows[:limit] if limit else rows


def by_slug(request, slug):
    for c in MockStore(request).get("discovery_candidates"):
        if c["slug"] == slug:
            return c
    return None


def tone_class(candidate):
    return DISCOVERY_TONES.get(candidate.get("tone"), DISCOVERY_TONES["blue"])


def cluster_cards(request, active_cluster=None):
    """Cluster filter cards with live non-dismissed counts (discovery.tsx)."""
    candidates = [
        c
        for c in MockStore(request).get("discovery_candidates")
        if c["status"] != "dismissed"
    ]
    return [
        {
            "id": c["id"],
            "label": c["label"],
            "count": sum(1 for x in candidates if x["cluster"] == c["id"]),
            "active": active_cluster == c["id"],
        }
        for c in DISCOVERY_CLUSTERS
    ]
