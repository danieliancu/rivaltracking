"""Discovery page, fragments, and mutations."""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_index_renders(client):
    response = client.get(reverse("discovery:index"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Discovery" in content
    assert "Find competitors you are not monitoring yet, ranked by catalogue similarity." in content
    assert "Discovery results" in content
    assert "Companies similar to your monitored competitors." in content
    # Cluster cards with live counts (seed: 2 Educational, 2 Outdoor, 2 General).
    assert "Educational Toys" in content
    assert "2 potential competitors" in content
    # Rows show "{match}% match · {cluster}".
    assert "82% match · Educational Toys" in content
    assert "68% catalogue overlap" in content


def test_index_cluster_filter(client):
    response = client.get(reverse("discovery:index"), {"cluster": "Outdoor Toys"})
    content = response.content.decode()
    assert response.status_code == 200
    assert "Filtered to Outdoor Toys" in content
    assert "Clear" in content
    assert "KidsPlayStore.co.uk" in content
    assert "BrightKidsPlay.com" not in content


def test_index_results_fragment(client):
    response = client.get(
        reverse("discovery:index"),
        HTTP_HX_REQUEST="true",
        HTTP_HX_TARGET="discovery-results",
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert 'id="discovery-results"' in content
    assert "<h1" not in content


def test_index_clusters_fragment(client):
    response = client.get(
        reverse("discovery:index"),
        HTTP_HX_REQUEST="true",
        HTTP_HX_TARGET="discovery-clusters",
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert 'id="discovery-clusters"' in content
    assert 'id="discovery-results"' not in content


def test_dialog_fragment(client):
    response = client.get(reverse("discovery:dialog"))
    content = response.content.decode()
    assert response.status_code == 200
    assert "Discover competitors" in content
    assert "Discovery mode" in content
    assert "Based on existing competitors" in content
    assert "Start discovery" in content


def test_run_returns_staged_fragment_and_toast(client):
    response = client.post(reverse("discovery:run"))
    content = response.content.decode()
    assert response.status_code == 200
    assert "stagedProgress(4, 700, 'discovery:changed')" in content
    assert "Analysing your market" in content
    assert "Ranking matches" in content
    assert "Discovery complete" in content
    assert "6 suggestions refreshed." in content


def test_why_match_drawer(client):
    response = client.get(reverse("discovery:why_match", kwargs={"slug": "brightkidsplay-com"}))
    content = response.content.decode()
    assert response.status_code == 200
    assert "BrightKidsPlay.com" in content
    assert "Why this match?" in content
    assert "82% match" in content
    assert "Match evidence" in content
    assert "Catalogue profile" in content
    assert "1,620" in content
    assert "Educational Toys (540)" in content
    assert "Monitor BrightKidsPlay.com" in content


def test_compare_drawer(client):
    response = client.get(reverse("discovery:compare", kwargs={"slug": "toycorner-co-uk"}))
    content = response.content.decode()
    assert response.status_code == 200
    assert "ToyCorner.co.uk vs ToyWorld.co.uk" in content
    assert "Catalogue profile comparison" in content
    assert "61% catalogue overlap" in content
    assert "2,210" in content
    assert "2,438" in content
    assert "£5 – £250" in content


def test_monitor_page_variant(client):
    response = client.post(
        reverse("discovery:monitor", kwargs={"slug": "brightkidsplay-com"}),
        {"variant": "page"},
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert "Monitoring" in content
    assert "82% match · Educational Toys" in content
    assert "Competitor added" in content
    assert "Now monitoring BrightKidsPlay.com — initial snapshot queued." in content


def test_monitor_default_variant_keeps_dashboard_row(client):
    response = client.post(reverse("discovery:monitor", kwargs={"slug": "toycorner-co-uk"}))
    content = response.content.decode()
    assert response.status_code == 200
    assert "Monitoring" in content
    assert "Competitor added" in content
    # Dashboard row has no cluster sub-line.
    assert "79% match · General Toys" not in content


def test_monitor_unknown_slug_404(client):
    response = client.post(reverse("discovery:monitor", kwargs={"slug": "nope"}))
    assert response.status_code == 404


def test_dismiss_removes_row(client):
    response = client.post(reverse("discovery:dismiss", kwargs={"slug": "brightkidsplay-com"}))
    content = response.content.decode()
    assert response.status_code == 200
    assert "Suggestion dismissed" in content
    assert "BrightKidsPlay.com" not in content
    assert 'id="discovery-results"' in content
    # OOB cluster counts refresh: Educational Toys drops to 1.
    assert "1 potential competitor" in content
    # Candidate stays in the store as dismissed.
    followup = client.get(reverse("discovery:index"))
    assert "BrightKidsPlay.com" not in followup.content.decode()


def test_not_relevant_removes_candidate(client):
    response = client.post(reverse("discovery:not_relevant", kwargs={"slug": "toycorner-co-uk"}))
    content = response.content.decode()
    assert response.status_code == 200
    assert "Feedback saved" in content
    assert "ToyCorner.co.uk will no longer be suggested." in content
    followup = client.get(reverse("discovery:index"))
    assert "ToyCorner.co.uk" not in followup.content.decode()


def test_empty_state_after_dismissing_all(client):
    for slug in (
        "brightkidsplay-com",
        "toycorner-co-uk",
        "kidsplaystore-co-uk",
        "smartplaytoys-co-uk",
        "gardenplaydirect-com",
        "littleexplorers-co-uk",
    ):
        client.post(reverse("discovery:dismiss", kwargs={"slug": slug}))
    response = client.get(reverse("discovery:index"))
    content = response.content.decode()
    assert "No discoveries yet" in content
    assert "Add competitor by URL" in content
    assert "0 potential competitors" in content


def test_run_restores_dismissed(client):
    client.post(reverse("discovery:dismiss", kwargs={"slug": "brightkidsplay-com"}))
    response = client.post(reverse("discovery:run"))
    assert response.status_code == 200
    followup = client.get(reverse("discovery:index"))
    assert "BrightKidsPlay.com" in followup.content.decode()
