"""Discovery reads over the mock store."""
from apps.core.mock.store import MockStore

# Candidate tone → identity tile classes (company-discovery-row.tsx).
DISCOVERY_TONES = {
    "blue": "bg-info/10 text-info",
    "purple": "bg-purple/10 text-purple",
    "teal": "bg-teal/10 text-teal",
    "orange": "bg-warning/10 text-warning",
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
