"""End-to-end own-catalogue loop on a fresh (non-seeded) workspace:
connect website → import → add competitor → scan → match → real comparison."""
from decimal import Decimal

import pytest

from apps.accounts.services import register_account
from apps.catalogue import selectors as catalogue_selectors
from apps.catalogue.importing import import_from_website
from apps.catalogue.models import OwnCatalogueSource, OwnProduct
from apps.competitors.models import Competitor
from apps.scanning import services as scan_services
from apps.scanning.tests.test_scraping import FakeFetcher

pytestmark = pytest.mark.django_db

GTIN = "5099999999901"


def _product_html(name, sku, price, gtin, availability="InStock"):
    return f"""<html><head><script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"Product","name":"{name}","sku":"{sku}",
     "gtin13":"{gtin}","offers":{{"@type":"Offer","price":"{price}","priceCurrency":"GBP",
       "availability":"https://schema.org/{availability}"}}}}
    </script></head><body></body></html>"""


def _site(base, path):
    return FakeFetcher({
        base: (200, "<html></html>"),
        f"{base}/robots.txt": (404, ""),
        f"{base}/sitemap.xml": (200,
            f'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'<url><loc>{base}{path}</loc></url></urlset>'),
    })


@pytest.fixture
def fresh_ws(db):
    _user, ws = register_account(email="loop@demo.test", password="loop-pass-12345", workspace_name="Loop Co")
    return ws


def test_own_vs_competitor_loop(fresh_ws):
    ws = fresh_ws

    # 1. Connect + import own website (our price £18).
    own_base = "https://mystore.example"
    own_fetcher = _site(own_base, "/products/widget")
    own_fetcher.pages[f"{own_base}/products/widget"] = (200, _product_html("Super Widget", "OWN-W", "18.00", GTIN))
    source = OwnCatalogueSource.objects.create(
        workspace=ws, source_type=OwnCatalogueSource.SourceType.WEBSITE,
        website_url=own_base, domain="mystore.example",
    )
    import_from_website(source, fetcher=own_fetcher, throttle=False)
    assert OwnProduct.objects.for_workspace(ws).filter(own_sku="OWN-W").exists()

    # 2. Add a competitor and scan it (same GTIN, £22).
    competitor = Competitor.objects.create(
        workspace=ws, name="Rival Store", slug="rival-store",
        domain="rival.example", website_url="https://rival.example",
        status=Competitor.Status.HEALTHY, monitoring_enabled=True,
    )
    comp_fetcher = _site("https://rival.example", "/products/widget")
    comp_fetcher.pages["https://rival.example/products/widget"] = (200, _product_html("Super Widget", "RV-W", "22.00", GTIN))
    job = scan_services.create_scan_job(competitor)
    scan_services.execute_scan_job(job.id, fetcher=comp_fetcher)

    # 3. Matching converged own + competitor on one canonical product.
    own = OwnProduct.objects.get(workspace=ws, own_sku="OWN-W")
    assert own.product is not None
    assert own.product.listings.filter(competitor=competitor).exists()

    # 4. Real price position: we (£18) are cheaper than the competitor (£22).
    pos = catalogue_selectors.price_position(own)
    assert pos["competitors"] == 1
    assert pos["our_price"] == 18.0
    assert pos["lowest"] == 22.0
    assert pos["position"] == "cheapest"
