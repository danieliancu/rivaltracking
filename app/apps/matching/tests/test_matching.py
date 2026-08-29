"""Deterministic matching hierarchy, auto-merge, and own-catalogue metrics."""
from decimal import Decimal

import pytest

from apps.catalogue import selectors as catalogue_selectors
from apps.catalogue.models import OwnProduct, Product, ProductListing, StockStatus
from apps.competitors.models import Competitor
from apps.matching import engine
from apps.matching.models import MatchResult

pytestmark = pytest.mark.django_db


def _competitors(workspace):
    return list(Competitor.objects.for_workspace(workspace)[:2])


def _listing(workspace, competitor, *, name, slug, price, gtin="", mpn="", brand="", sku="", stock=StockStatus.IN_STOCK):
    product = Product.objects.create(
        workspace=workspace, name=name, slug=slug, gtin=gtin, mpn=mpn, brand=brand, sku=sku
    )
    listing = ProductListing.objects.create(
        workspace=workspace, product=product, competitor=competitor,
        competitor_product_name=name, current_price=Decimal(str(price)),
        current_stock_status=stock, is_primary=True,
    )
    return product, listing


def test_gtin_match_auto_merges(workspace):
    a, b = _competitors(workspace)
    pa, la = _listing(workspace, a, name="LEGO Castle", slug="lego-a", price=49.99, gtin="5702016367546")
    pb, lb = _listing(workspace, b, name="LEGO Castle Set", slug="lego-b", price=52.99, gtin="5702016367546")

    result = engine.match_listing(lb)
    assert result.status == MatchResult.Status.AUTO_MATCHED
    assert result.method == MatchResult.Method.GTIN
    assert result.confidence == 99.0

    lb.refresh_from_db()
    assert lb.product_id == pa.id
    assert not Product.objects.filter(id=pb.id).exists()  # orphan merged away
    assert pa.listings.count() == 2


def test_title_similarity_auto_merges_identical(workspace):
    a, b = _competitors(workspace)
    pa, la = _listing(workspace, a, name="Zzqwx Unique Gadget 12345", slug="uniq-a", price=10)
    pb, lb = _listing(workspace, b, name="Zzqwx Unique Gadget 12345", slug="uniq-b", price=12)
    result = engine.match_listing(lb)
    assert result.status == MatchResult.Status.AUTO_MATCHED
    assert result.method == MatchResult.Method.TITLE
    lb.refresh_from_db()
    assert lb.product_id == pa.id


def test_no_match_is_unmatched(workspace):
    a, _ = _competitors(workspace)
    _, listing = _listing(workspace, a, name="Zzqwx Wholly Unrelated Thing 98765", slug="uniq-z", price=5)
    result = engine.match_listing(listing)
    assert result.status == MatchResult.Status.UNMATCHED


def test_match_results_are_workspace_isolated(workspace, other_workspace):
    a, _ = _competitors(workspace)
    _, listing = _listing(workspace, a, name="Zzqwx Unique Gadget 12345", slug="uniq-a", price=10)
    engine.match_listing(listing)
    assert MatchResult.objects.for_workspace(other_workspace).count() == 0


def test_own_catalogue_price_position(workspace):
    a, b = _competitors(workspace)
    pa, la = _listing(workspace, a, name="Zzqwx Widget", slug="w-a", price=20, gtin="1111111111116")
    pb, lb = _listing(workspace, b, name="Zzqwx Widget", slug="w-b", price=25, gtin="1111111111116")
    engine.match_listing(lb)  # merge into pa → pa has both listings (20, 25)

    own = OwnProduct.objects.create(
        workspace=workspace, product=pa, name="Our Widget", own_sku="OWN-1",
        our_price=Decimal("18.00"),
    )
    pos = catalogue_selectors.price_position(own)
    assert pos["competitors"] == 2
    assert pos["lowest"] == 20.0
    assert pos["our_price"] == 18.0
    assert pos["position"] == "cheapest"
    assert pos["diff_vs_lowest_pct"] == -10.0
