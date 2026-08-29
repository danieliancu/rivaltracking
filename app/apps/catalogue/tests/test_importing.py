"""Own-catalogue website import + own-product matching (offline fixtures)."""
from decimal import Decimal

import pytest

from apps.catalogue.importing import import_from_website
from apps.catalogue.models import OwnCatalogueSource, OwnProduct, Product, ProductListing, StockStatus
from apps.competitors.models import Competitor
from apps.matching.engine import match_own_product
from apps.scanning.tests.test_scraping import FakeFetcher

pytestmark = pytest.mark.django_db

BASE = "https://mystore.example"
SITEMAP = f"""<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE}/products/widget-a</loc></url>
  <url><loc>{BASE}/products/widget-b</loc></url>
</urlset>"""


def _p(name, sku, price, gtin=""):
    gtin_line = f'"gtin13":"{gtin}",' if gtin else ""
    return f"""<html><head><script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"Product","name":"{name}","sku":"{sku}",
     {gtin_line}
     "offers":{{"@type":"Offer","price":"{price}","priceCurrency":"GBP",
       "availability":"https://schema.org/InStock"}}}}
    </script></head><body></body></html>"""


def _source(workspace):
    return OwnCatalogueSource.objects.create(
        workspace=workspace, source_type=OwnCatalogueSource.SourceType.WEBSITE,
        website_url=BASE, domain="mystore.example",
    )


def _fake():
    return FakeFetcher({
        BASE: (200, "<html></html>"),
        f"{BASE}/robots.txt": (404, ""),
        f"{BASE}/sitemap.xml": (200, SITEMAP),
        f"{BASE}/products/widget-a": (200, _p("Acme Widget A", "OWN-A", "18.00", "5011111111111")),
        f"{BASE}/products/widget-b": (200, _p("Acme Widget B", "OWN-B", "42.50")),
    })


def test_website_import_populates_own_catalogue(workspace):
    source = _source(workspace)
    import_from_website(source, fetcher=_fake(), throttle=False)
    source.refresh_from_db()
    assert source.status == OwnCatalogueSource.Status.CONNECTED
    assert source.products_found == 2

    own = OwnProduct.objects.get(workspace=workspace, own_sku="OWN-A")
    assert own.our_price == Decimal("18.00")
    assert own.gtin == "5011111111111"
    assert own.in_stock is True
    assert own.product is not None
    assert own.listings.filter(channel="website").exists()


def test_own_product_matches_existing_competitor_canonical(workspace):
    competitor = Competitor.objects.for_workspace(workspace).first()
    canonical = Product.objects.create(
        workspace=workspace, name="Shared Gadget", slug="shared-gadget-x", gtin="5099999999999",
    )
    ProductListing.objects.create(
        workspace=workspace, product=canonical, competitor=competitor,
        current_price=Decimal("25.00"), current_stock_status=StockStatus.IN_STOCK, is_primary=True,
    )
    own = OwnProduct.objects.create(
        workspace=workspace, name="Shared Gadget", own_sku="OWN-SG", gtin="5099999999999",
        our_price=Decimal("21.00"),
    )
    match_own_product(own)
    own.refresh_from_db()
    assert own.product_id == canonical.id


def test_import_is_workspace_isolated(workspace, other_workspace):
    import_from_website(_source(workspace), fetcher=_fake(), throttle=False)
    assert OwnProduct.objects.for_workspace(other_workspace).filter(own_sku="OWN-A").count() == 0
    assert OwnProduct.objects.for_workspace(workspace).filter(own_sku="OWN-A").count() == 1
