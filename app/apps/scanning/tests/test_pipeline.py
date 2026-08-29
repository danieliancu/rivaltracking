"""End-to-end persistence: baseline scan, then a change scan producing history
and ChangeEvents; plus change-aware snapshots and detection idempotency."""
from decimal import Decimal

import pytest

from apps.catalogue import services as catalogue_services
from apps.catalogue.models import PriceSnapshot, Product, ProductListing, StockStatus
from apps.changes import detection
from apps.changes.models import ChangeEvent
from apps.competitors.models import Competitor
from apps.scanning import services
from apps.scanning.tests.test_scraping import FakeFetcher

pytestmark = pytest.mark.django_db

BASE = "https://teststore.example"
SITEMAP = f"""<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE}/products/widget</loc></url>
</urlset>"""


def _product_html(price, availability="InStock"):
    return f"""<html><head><script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"Product","name":"Test Widget",
     "sku":"TS-1","gtin13":"1234567890123","offers":{{"@type":"Offer",
     "price":"{price}","priceCurrency":"GBP","availability":"https://schema.org/{availability}"}}}}
    </script></head><body></body></html>"""


def _fake(price, availability="InStock"):
    return FakeFetcher({
        BASE: (200, "<html></html>"),
        f"{BASE}/robots.txt": (404, ""),
        f"{BASE}/sitemap.xml": (200, SITEMAP),
        f"{BASE}/products/widget": (200, _product_html(price, availability)),
    })


@pytest.fixture
def competitor(workspace):
    return Competitor.objects.create(
        workspace=workspace, name="Test Store", slug="test-store",
        domain="teststore.example", website_url=BASE, monitoring_enabled=True,
        status=Competitor.Status.HEALTHY,
    )


def _scan(competitor, fetcher):
    job = services.create_scan_job(competitor)
    services.execute_scan_job(job.id, fetcher=fetcher)
    job.refresh_from_db()
    return job


def test_baseline_scan_creates_listing_without_change_events(competitor, workspace):
    job = _scan(competitor, _fake("24.99"))
    assert job.status == "completed"
    listing = ProductListing.objects.get(competitor=competitor)
    assert listing.current_price == Decimal("24.99")
    assert listing.current_stock_status == StockStatus.IN_STOCK
    assert PriceSnapshot.objects.filter(listing=listing).count() == 1
    # Baseline: no change events on the first completed scan.
    assert ChangeEvent.objects.filter(competitor=competitor).count() == 0


def test_second_scan_detects_price_drop_and_stock_out(competitor, workspace):
    _scan(competitor, _fake("24.99"))
    job2 = _scan(competitor, _fake("19.99", availability="OutOfStock"))
    assert job2.changes_detected >= 2

    listing = ProductListing.objects.get(competitor=competitor)
    assert listing.current_price == Decimal("19.99")
    assert PriceSnapshot.objects.filter(listing=listing).count() == 2

    drop = ChangeEvent.objects.get(competitor=competitor, event_type=ChangeEvent.Type.PRICE_DECREASE)
    assert drop.secondary == "-20.0%"
    assert drop.impact == ChangeEvent.Impact.HIGH
    assert ChangeEvent.objects.filter(
        competitor=competitor, event_type=ChangeEvent.Type.STOCK_OUT
    ).exists()


def test_change_aware_snapshots_skip_duplicates(competitor):
    _scan(competitor, _fake("24.99"))
    listing = ProductListing.objects.get(competitor=competitor)
    # Same price again → no new snapshot.
    assert catalogue_services.record_price_snapshot(listing) is None


def test_detection_is_idempotent(competitor):
    _scan(competitor, _fake("24.99"))
    listing = ProductListing.objects.get(competitor=competitor)
    listing.previous_price = Decimal("24.99")
    listing.current_price = Decimal("19.99")
    listing.save()
    from django.utils import timezone

    previous = {"price": Decimal("24.99"), "stock": listing.current_stock_status,
                "promotion": "", "title": listing.competitor_product_name, "category": ""}
    now = timezone.now()
    first = detection.detect_for_listing(listing, previous, detected_at=now)
    second = detection.detect_for_listing(listing, previous, detected_at=now)
    assert len(first) == 1 and second == []


def test_removed_after_repeated_misses(competitor, settings):
    settings.LISTING_MISSES_BEFORE_REMOVED = 2
    _scan(competitor, _fake("24.99"))
    # Product disappears from the catalogue (empty sitemap).
    other_html = """<html><head><script type="application/ld+json">
    {"@context":"https://schema.org","@type":"Product","name":"Other Thing",
     "sku":"TS-2","gtin13":"9999999999999","offers":{"@type":"Offer",
     "price":"5.00","priceCurrency":"GBP","availability":"https://schema.org/InStock"}}
    </script></head><body></body></html>"""
    empty = FakeFetcher({
        BASE: (200, "<html></html>"),
        f"{BASE}/robots.txt": (404, ""),
        f"{BASE}/sitemap.xml": (200, '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>%s/products/other</loc></url></urlset>' % BASE),
        f"{BASE}/products/other": (200, other_html),
    })
    _scan(competitor, empty)  # miss #1 — not removed yet
    listing = ProductListing.objects.get(competitor=competitor, competitor_sku="TS-1")
    assert listing.active is True and listing.consecutive_misses == 1
    _scan(competitor, empty)  # miss #2 — removed
    listing.refresh_from_db()
    assert listing.active is False
    assert ChangeEvent.objects.filter(
        listing=listing, event_type=ChangeEvent.Type.PRODUCT_REMOVED
    ).exists()
