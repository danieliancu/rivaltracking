import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

SLUG = "toyworld-co-uk"


def test_index_renders(client):
    response = client.get(reverse("competitors:index"))
    assert response.status_code == 200
    body = response.content.decode()
    assert "Monitored Competitors" in body
    assert "Portfolio Intelligence" in body
    assert "Monitoring Health" in body


def test_detail_real_slug(client):
    response = client.get(reverse("competitors:detail", args=[SLUG]))
    assert response.status_code == 200
    assert "ToyWorld.co.uk" in response.content.decode()


def test_detail_products_tab(client):
    response = client.get(reverse("competitors:detail", args=[SLUG]), {"tab": "products"})
    assert response.status_code == 200
    assert "Product Catalogue" in response.content.decode()


def test_detail_price_history_tab(client):
    response = client.get(
        reverse("competitors:detail", args=[SLUG]), {"tab": "price-history"}
    )
    assert response.status_code == 200
    assert "Price Change Events" in response.content.decode()


def test_detail_ai_analysis_tab(client):
    response = client.get(
        reverse("competitors:detail", args=[SLUG]), {"tab": "ai-analysis"}
    )
    assert response.status_code == 200
    body = response.content.decode()
    assert "AI Analysis — ToyWorld.co.uk" in body
    assert "Evidence — Recent Changes" in body


def test_detail_not_found(client):
    response = client.get(reverse("competitors:detail", args=["nope"]))
    assert response.status_code == 200
    assert "Competitor not found" in response.content.decode()


def test_add_dialog(client):
    response = client.get(reverse("competitors:add_dialog"))
    assert response.status_code == 200
    assert "Monitor a competitor" in response.content.decode()


def test_add_valid_url_returns_scanning(client):
    response = client.post(reverse("competitors:add"), {"url": "toyplanet.co.uk"})
    assert response.status_code == 200
    body = response.content.decode()
    assert "successfully added" in body
    assert "Detecting website" in body


def test_add_invalid_url_shows_error(client):
    response = client.post(reverse("competitors:add"), {"url": "not a url"})
    assert response.status_code == 200
    assert "valid website address" in response.content.decode()


def test_add_duplicate_url_shows_error(client):
    response = client.post(reverse("competitors:add"), {"url": "toyworld.co.uk"})
    assert response.status_code == 200
    assert "already monitoring" in response.content.decode()


def test_run_scan(client):
    response = client.post(reverse("competitors:run_scan", args=[SLUG]))
    assert response.status_code == 200
    assert "Scan complete" in response.content.decode()


def test_pause(client):
    response = client.post(reverse("competitors:pause_resume", args=[SLUG]))
    assert response.status_code == 200
    assert "Monitoring paused" in response.content.decode()


def test_remove(client):
    response = client.post(reverse("competitors:remove", args=[SLUG]))
    assert response.status_code == 200
    assert "Competitor removed" in response.content.decode()


def test_monitoring_drawer(client):
    response = client.get(reverse("competitors:monitoring_drawer", args=[SLUG]))
    assert response.status_code == 200
    body = response.content.decode()
    assert "Monitoring settings" in body
    assert "Track prices" in body


def test_save_monitoring(client):
    response = client.post(
        reverse("competitors:save_monitoring", args=[SLUG]),
        {"frequency": "Every 12 hours", "track_prices": "on"},
    )
    assert response.status_code == 200
    assert "Settings saved" in response.content.decode()


def test_products_fragment(client):
    response = client.get(reverse("competitors:products_fragment", args=[SLUG]))
    assert response.status_code == 200
    assert "products-table" in response.content.decode()
