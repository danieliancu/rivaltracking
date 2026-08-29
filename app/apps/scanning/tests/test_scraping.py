"""Extraction, normalisation, adapter selection and the scan orchestrator,
driven entirely from HTML/JSON-LD fixtures via a fake fetcher (no network)."""
from decimal import Decimal

import pytest
from bs4 import BeautifulSoup

from apps.catalogue.models import StockStatus
from apps.competitors.models import Competitor
from apps.scanning.scraping.adapters.registry import select_adapter
from apps.scanning.scraping.extractors.dom import DomExtractor
from apps.scanning.scraping.extractors.jsonld import JsonLdExtractor
from apps.scanning.scraping.fetchers.base import FetchResult
from apps.scanning.scraping.normalizers.base import (
    normalize,
    normalize_stock,
    parse_price,
)
from apps.scanning.scraping.orchestration import run_competitor_scan, scrape_url

pytestmark = pytest.mark.django_db

JSONLD_HTML = """
<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Product","name":"LEGO Castle Set",
 "brand":{"@type":"Brand","name":"LEGO"},"sku":"TW-10432","gtin13":"5702016367546",
 "category":"Construction Toys","image":"https://ex.com/lego.jpg",
 "offers":{"@type":"Offer","price":"24.99","priceCurrency":"GBP",
           "availability":"https://schema.org/InStock"}}
</script></head><body><h1>LEGO Castle Set</h1></body></html>
"""

OOS_JSONLD_HTML = JSONLD_HTML.replace("InStock", "OutOfStock").replace("24.99", "89.00")

DOM_HTML = """
<html><head>
<meta property="og:title" content="Wooden Balance Bike">
<meta property="product:price:amount" content="89.00">
<meta property="product:price:currency" content="GBP">
<meta property="product:availability" content="in stock">
<meta property="og:image" content="https://ex.com/bike.jpg">
<link rel="canonical" href="https://toyworld.co.uk/products/bike">
</head><body></body></html>
"""

SHOPIFY_HTML = '<html><head><script>var x="cdn.shopify.com/s/files"</script></head><body></body></html>'
WOO_HTML = '<html><body class="woocommerce-page"></body></html>'

SITEMAP_XML = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://toyworld.co.uk/products/lego</loc></url>
  <url><loc>https://toyworld.co.uk/products/bike</loc></url>
  <url><loc>https://toyworld.co.uk/about</loc></url>
</urlset>
"""


class FakeFetcher:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def fetch(self, url):
        self.calls.append(url)
        if url in self.pages:
            status, text = self.pages[url]
            return FetchResult(url=url, status_code=status, text=text, final_url=url, ok=status < 400)
        return FetchResult(url=url, status_code=404, ok=False)

    def close(self):
        pass


# --- extractors -------------------------------------------------------------

def test_jsonld_extractor():
    soup = BeautifulSoup(JSONLD_HTML, "html.parser")
    product = JsonLdExtractor().extract(FetchResult(url="u", status_code=200, ok=True), soup)
    assert product is not None and product.is_usable()
    assert product.title == "LEGO Castle Set"
    assert product.brand == "LEGO"
    assert product.price == "24.99"
    assert product.gtin == "5702016367546"
    assert product.stock_status == "InStock"


def test_dom_extractor_fallback():
    soup = BeautifulSoup(DOM_HTML, "html.parser")
    product = DomExtractor().extract(FetchResult(url="u", status_code=200, ok=True), soup)
    assert product is not None
    assert product.title == "Wooden Balance Bike"
    assert product.price == "89.00"


# --- normalisation ----------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("£49.99", Decimal("49.99")),
    ("1,299.00", Decimal("1299.00")),
    ("19,99", Decimal("19.99")),
    ("", None),
    ("out of stock", None),
])
def test_parse_price(raw, expected):
    assert parse_price(raw) == expected


def test_normalize_stock():
    assert normalize_stock("InStock") == StockStatus.IN_STOCK
    assert normalize_stock("https://schema.org/OutOfStock".rsplit("/", 1)[-1]) == StockStatus.OUT_OF_STOCK
    assert normalize_stock("") == StockStatus.UNKNOWN


def test_normalize_full():
    soup = BeautifulSoup(JSONLD_HTML, "html.parser")
    extracted = JsonLdExtractor().extract(FetchResult(url="u", status_code=200, ok=True), soup)
    n = normalize(extracted)
    assert n.price == Decimal("24.99")
    assert n.currency == "GBP"
    assert n.stock_status == StockStatus.IN_STOCK
    assert n.gtin == "5702016367546"


# --- adapters ---------------------------------------------------------------

def test_adapter_selection():
    assert select_adapter(FetchResult(url="u", status_code=200, text=SHOPIFY_HTML, ok=True)).name == "shopify"
    assert select_adapter(FetchResult(url="u", status_code=200, text=WOO_HTML, ok=True)).name == "woocommerce"
    assert select_adapter(FetchResult(url="u", status_code=200, text="<html></html>", ok=True)).name == "generic"


def test_scrape_url_end_to_end():
    fake = FakeFetcher({"https://toyworld.co.uk/products/lego": (200, JSONLD_HTML)})
    result, normalized = scrape_url("https://toyworld.co.uk/products/lego", fake)
    assert result.ok
    assert normalized.title == "LEGO Castle Set"
    assert normalized.price == Decimal("24.99")


# --- orchestrator -----------------------------------------------------------

def test_orchestrator_discovers_and_scrapes(workspace):
    competitor = Competitor.objects.for_workspace(workspace).get(slug="toyworld-co-uk")
    base = "https://toyworld.co.uk"
    fake = FakeFetcher({
        base: (200, "<html></html>"),
        f"{base}/robots.txt": (404, ""),
        f"{base}/sitemap.xml": (200, SITEMAP_XML),
        f"{base}/products/lego": (200, JSONLD_HTML),
        f"{base}/products/bike": (200, DOM_HTML),
    })
    outcome = run_competitor_scan(competitor, fetcher=fake, throttle=False)
    assert outcome.pages_requested == 2  # /about filtered out by is_product_url
    assert outcome.products_found == 2
    assert {i.normalized.title for i in outcome.items} == {"LEGO Castle Set", "Wooden Balance Bike"}

    from apps.scanning.models import DiscoveredUrl, RawCapture

    assert DiscoveredUrl.objects.filter(competitor=competitor, status="active").count() == 2
    assert RawCapture.objects.filter(competitor=competitor).count() == 2
