"""Products index / details pages, fragments and mutations."""
import pytest
from django.urls import reverse

from apps.core.mock.store import SESSION_KEY

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Index page

def test_index_renders_landmarks(client):
    response = client.get(reverse("products:index"))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Products" in html
    assert "Explore and compare products detected across your monitored competitors." in html
    assert "AI Product Intelligence" in html
    assert "Price Movement" in html
    assert "Most Active Categories" in html
    assert "Product Catalogue" in html
    assert "LEGO Castle Set" in html
    # KPI row
    assert "Total products" in html and "8,746" in html


def test_index_filters_by_query_and_competitor(client):
    response = client.get(reverse("products:index"), {"q": "lego"})
    html = response.content.decode()
    assert "LEGO Castle Set" in html
    assert "Unicorn Plush XL" not in html

    response = client.get(reverse("products:index"), {"competitor": "playnest-co-uk"})
    html = response.content.decode()
    assert "Unicorn Plush XL" in html
    assert "LEGO Castle Set" not in html


def test_index_change_and_stock_filters(client):
    response = client.get(reverse("products:index"), {"change": "price-decrease"})
    html = response.content.decode()
    assert "LEGO Castle Set" in html
    assert "STEM Robot Kit" not in html

    response = client.get(reverse("products:index"), {"stock": "out"})
    html = response.content.decode()
    assert "Wooden Balance Bike" in html
    assert "LEGO Castle Set" not in html


def test_index_no_matches_empty_state(client):
    response = client.get(reverse("products:index"), {"q": "zzz-no-such"})
    html = response.content.decode()
    assert "No products found" in html
    assert "Try changing your filters or search query." in html


def test_index_fragment_returns_partial_with_canonical_push_url(client):
    response = client.get(
        reverse("products:index"),
        {"q": "lego", "competitor": "", "category": "", "change": "all", "stock": "all",
         "range": "30d", "sort": "recent"},
        HTTP_HX_REQUEST="true",
        HTTP_HX_TARGET="products-table",
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert "<html" not in html  # partial only
    assert 'id="products-table"' in html
    assert response["HX-Push-Url"] == reverse("products:index") + "?q=lego"


def test_index_sorting(client):
    response = client.get(reverse("products:index"), {"sort": "price-high"})
    html = response.content.decode()
    # Wooden Balance Bike (£89.00) is the most expensive seed product.
    assert html.index("Wooden Balance Bike") < html.index("LEGO Castle Set")


# ---------------------------------------------------------------------------
# CSV export

def test_export_csv(client):
    response = client.get(reverse("products:export"), {"q": "lego"})
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert 'filename="rivaltracking-products.csv"' in response["Content-Disposition"]
    body = response.content.decode()
    assert body.splitlines()[0].startswith("Name,SKU,Competitor,Category")
    assert "LEGO Castle Set" in body
    assert "Unicorn Plush XL" not in body


def test_export_csv_selected_rows(client):
    response = client.get(
        reverse("products:export"), {"selected": ["lego-castle-set", "stem-robot-kit"]}
    )
    body = response.content.decode()
    assert "LEGO Castle Set" in body and "STEM Robot Kit" in body
    assert "Wooden Balance Bike" not in body


# ---------------------------------------------------------------------------
# Detail page

def test_detail_overview(client):
    response = client.get(reverse("products:detail", kwargs={"slug": "lego-castle-set"}))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Back to products" in html
    assert "LEGO Castle Set" in html
    assert "TW-10432 · ToyWorld.co.uk · Construction Toys" in html
    assert "Current price" in html and "Discovered" in html
    assert "Detected Events" in html
    assert "View supporting changes" in html
    assert "Compare 3 listings" in html
    assert "Create alert" in html and "Ask AI" in html


def test_detail_tabs(client):
    url = reverse("products:detail", kwargs={"slug": "lego-castle-set"})
    html = client.get(url, {"tab": "price-history"}).content.decode()
    assert "Price Movement" in html

    html = client.get(url, {"tab": "changes"}).content.decode()
    assert "View in Changes" in html

    html = client.get(url, {"tab": "comparison"}).content.decode()
    assert "Compare 3 competitor listings" in html

    html = client.get(url, {"tab": "ai-analysis"}).content.decode()
    assert "AI Analysis — LEGO Castle Set" in html
    assert "Ask AI about this product" in html


def test_detail_comparison_empty_state(client):
    url = reverse("products:detail", kwargs={"slug": "stem-robot-kit"})
    html = client.get(url, {"tab": "comparison"}).content.decode()
    assert "No matched listings" in html
    assert "Product matching has not found this product at other competitors yet." in html


def test_detail_not_found(client):
    response = client.get(reverse("products:detail", kwargs={"slug": "no-such-product"}))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Product not found" in html
    assert "This product is not in your monitored catalogue." in html


# ---------------------------------------------------------------------------
# Compare drawer fragments

def test_compare_drawer(client):
    response = client.get(reverse("products:compare_drawer", kwargs={"slug": "lego-castle-set"}))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Matched across 3 competitors" in html
    assert "Matched · 96% confidence" in html
    assert "Lowest price" in html
    assert "The lowest detected price is currently out of stock." in html


def test_compare_drawer_unmatched_404(client):
    response = client.get(reverse("products:compare_drawer", kwargs={"slug": "stem-robot-kit"}))
    assert response.status_code == 404


def test_compare_selected(client):
    url = reverse("products:compare_selected")
    # Fewer than two → info toast.
    html = client.get(url, {"selected": ["lego-castle-set"]}).content.decode()
    assert "Select at least two products to compare." in html
    # No matched among selected → toast with description.
    html = client.get(url, {"selected": ["stem-robot-kit", "unicorn-plush-xl"]}).content.decode()
    assert "No matched listings" in html
    assert "The selected products have no matched competitor listings yet." in html
    # Matched present → drawer.
    html = client.get(url, {"selected": ["stem-robot-kit", "lego-castle-set"]}).content.decode()
    assert "Matched across 3 competitors" in html


# ---------------------------------------------------------------------------
# Watchlist mutations

def test_watchlist_toggle(client):
    url = reverse("products:watchlist_toggle", kwargs={"slug": "lego-castle-set"})
    response = client.post(url)
    html = response.content.decode()
    assert response.status_code == 200
    assert "Added to watchlist" in html
    assert "fill-current" in html
    assert client.session[SESSION_KEY]["watchlist"] == ["lego-castle-set"]

    html = client.post(url).content.decode()
    assert "Removed from watchlist" in html
    assert client.session[SESSION_KEY]["watchlist"] == []


def test_watchlist_bulk_add(client):
    url = reverse("products:watchlist_add")
    response = client.post(url, {"selected": ["lego-castle-set", "stem-robot-kit"]})
    html = response.content.decode()
    assert response.status_code == 200
    assert "2 products added to watchlist" in html
    assert 'id="products-table"' in html
    assert sorted(client.session[SESSION_KEY]["watchlist"]) == [
        "lego-castle-set",
        "stem-robot-kit",
    ]

    html = client.post(url, {"selected": ["lego-castle-set"]}).content.decode()
    assert "Already on your watchlist" in html
