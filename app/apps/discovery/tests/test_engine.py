"""Discovery scoring + candidate lifecycle."""
import pytest

from apps.discovery import engine, services
from apps.discovery.models import DiscoveryCandidate

pytestmark = pytest.mark.django_db


def test_score_reflects_category_overlap(workspace):
    # The seeded catalogue includes "Construction Toys" and "Educational Toys".
    high, reasons, _ = engine.score_candidate(
        workspace, categories=["Construction Toys", "Educational Toys"]
    )
    low, _, _ = engine.score_candidate(workspace, categories=["Nonexistent Category"])
    assert high > low
    assert any("categor" in r for r in reasons)


def test_upsert_candidate_is_workspace_isolated(workspace, other_workspace):
    engine.upsert_candidate(workspace, name="Rival Co", domain="rival.example",
                            categories=["Construction Toys"], products=100)
    assert DiscoveryCandidate.objects.for_workspace(workspace).filter(domain="rival.example").exists()
    # The other workspace never sees this candidate.
    assert not DiscoveryCandidate.objects.for_workspace(other_workspace).filter(
        domain="rival.example"
    ).exists()


def test_monitor_candidate_creates_competitor(client, workspace):
    from apps.competitors.models import Competitor

    class Req:
        pass
    req = Req(); req.workspace = workspace
    services.monitor_candidate(req, "brightkidsplay-com")
    assert Competitor.objects.for_workspace(workspace).filter(slug="brightkidsplay-com").exists()
    assert DiscoveryCandidate.objects.get(workspace=workspace, slug="brightkidsplay-com").status == "monitoring"
