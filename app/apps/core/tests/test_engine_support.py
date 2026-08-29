"""Images scaffold + quotas usage/limits."""
import pytest

from apps.core import images, quotas

pytestmark = pytest.mark.django_db


def test_thumbnail_url_returns_source(workspace):
    from apps.catalogue.models import Product

    p = Product.objects.for_workspace(workspace).exclude(image_url="").first()
    assert images.thumbnail_url(p) == p.image_url


def test_image_store_key_is_stable():
    store = images.get_image_store()
    k1 = store.key_for("https://ex.com/a.jpg")
    k2 = store.key_for("https://ex.com/a.jpg")
    assert k1 == k2 and len(k1) == 32


def test_quota_usage_reports_counts(workspace):
    u = quotas.usage(workspace)
    assert u["competitors"] == 4
    assert u["products"] >= 10
    assert "ai_analyses_last_24h" in u


def test_within_limits(workspace):
    assert quotas.within_limits(workspace, "competitors") is True
    assert quotas.within_limits(workspace, "competitors", {"competitors": 1}) is False
    assert quotas.within_limits(workspace, "unknown_resource") is True
