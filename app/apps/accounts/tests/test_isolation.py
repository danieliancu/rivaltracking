"""Tenant isolation: a workspace must never read or mutate another's data.

Both fixtures seed identical slugs, so these tests plant an object that exists
ONLY in ``other_workspace`` and assert the signed-in ``client`` (a different
workspace) can neither see nor mutate it — and that lookups 404 / show the
"not in your workspace" state rather than leaking existence.
"""
import pytest
from django.urls import reverse

from apps.catalogue.models import Product, ProductListing, StockStatus
from apps.changes.models import ChangeEvent
from apps.competitors.models import Competitor

pytestmark = pytest.mark.django_db


def _secret_competitor(other_workspace):
    return Competitor.objects.create(
        workspace=other_workspace,
        name="Secret Rival Ltd",
        slug="secret-rival",
        domain="secret-rival.example",
        status=Competitor.Status.HEALTHY,
        products_count=999,
    )


def test_competitor_detail_does_not_leak_other_workspace(client, other_workspace):
    _secret_competitor(other_workspace)
    response = client.get(reverse("competitors:detail", kwargs={"slug": "secret-rival"}))
    html = response.content.decode()
    assert "Secret Rival Ltd" not in html
    assert "not monitored in your workspace" in html


def test_competitor_index_does_not_list_other_workspace(client, other_workspace):
    _secret_competitor(other_workspace)
    html = client.get(reverse("competitors:index")).content.decode()
    assert "Secret Rival Ltd" not in html


def test_competitor_mutation_on_foreign_slug_404s(client, other_workspace):
    _secret_competitor(other_workspace)
    response = client.post(reverse("competitors:pause_resume", kwargs={"slug": "secret-rival"}))
    assert response.status_code == 404
    # The foreign row is untouched.
    assert Competitor.objects.get(slug="secret-rival").status == Competitor.Status.HEALTHY


def test_product_detail_does_not_leak_other_workspace(client, other_workspace):
    product = Product.objects.create(
        workspace=other_workspace, name="Secret Gadget", slug="secret-gadget", sku="SG-1"
    )
    ProductListing.objects.create(
        workspace=other_workspace,
        product=product,
        competitor=Competitor.objects.for_workspace(other_workspace).first(),
        current_stock_status=StockStatus.IN_STOCK,
        is_primary=True,
    )
    response = client.get(reverse("products:detail", kwargs={"slug": "secret-gadget"}))
    html = response.content.decode()
    assert "Secret Gadget" not in html
    assert "not in your monitored catalogue" in html


def test_search_does_not_leak_other_workspace(client, other_workspace):
    Product.objects.create(
        workspace=other_workspace, name="Secret Gadget", slug="secret-gadget", sku="SG-1"
    )
    response = client.get(
        reverse("core:search"), {"q": "Secret Gadget"}, HTTP_HX_REQUEST="true"
    )
    # The slug only appears inside a real result link, never in the
    # "no results for …" echo of the query.
    assert "secret-gadget" not in response.content.decode()


def test_change_drawer_does_not_leak_other_workspace(client, other_workspace):
    event = ChangeEvent.objects.filter(workspace=other_workspace).first()
    response = client.get(reverse("changes:drawer", args=[event.id]))
    assert response.status_code == 404


def test_watchlist_toggle_on_foreign_product_is_noop(client, other_workspace):
    from apps.products.models import WatchlistItem

    Product.objects.create(
        workspace=other_workspace, name="Secret Gadget", slug="secret-gadget", sku="SG-1"
    )
    client.post(reverse("products:watchlist_toggle", kwargs={"slug": "secret-gadget"}))
    assert not WatchlistItem.objects.filter(product__slug="secret-gadget").exists()
