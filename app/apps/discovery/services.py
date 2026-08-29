"""Discovery mutations over the DiscoveryCandidate model. Starting monitoring
creates a real Competitor for the workspace."""
from django.utils import timezone

from apps.competitors.models import Competitor
from apps.core.entities import competitor_tone

from . import engine
from .models import DiscoveryCandidate


def _workspace(request):
    return getattr(request, "workspace", None)


def monitor_candidate(request, slug):
    """Future: POST /api/discovery/:id/monitor — flip to monitoring + create a Competitor."""
    candidate = DiscoveryCandidate.objects.for_workspace(_workspace(request)).filter(slug=slug).first()
    if candidate is None:
        return None
    candidate.status = DiscoveryCandidate.Status.MONITORING
    candidate.save(update_fields=["status", "updated_at"])

    now = timezone.now()
    products = candidate.catalogue_profile.get("products")
    Competitor.objects.get_or_create(
        workspace=candidate.workspace,
        slug=candidate.slug,
        defaults={
            "name": candidate.name,
            "domain": candidate.domain,
            "website_url": candidate.website_url or f"https://{candidate.domain}",
            "market": "UK Toys",
            "status": Competitor.Status.INITIALISING,
            "monitoring_enabled": True,
            "tone": competitor_tone(candidate.name),
            "products_count": products if isinstance(products, int) else None,
            "last_scan_at": now,
            "next_scan_at": now + timezone.timedelta(hours=24),
        },
    )
    from .selectors import candidate_dict

    return candidate_dict(candidate)


def dismiss_candidate(request, slug):
    """Future: POST /api/discovery/:id/dismiss"""
    DiscoveryCandidate.objects.for_workspace(_workspace(request)).filter(slug=slug).update(
        status=DiscoveryCandidate.Status.DISMISSED
    )


def mark_not_relevant(request, slug):
    """Future: POST /api/discovery/:id/feedback — remove the candidate."""
    DiscoveryCandidate.objects.for_workspace(_workspace(request)).filter(slug=slug).delete()


def run_discovery(request):
    """Future: POST /api/discovery/run — run a real discovery pass."""
    return engine.run_discovery(_workspace(request))
