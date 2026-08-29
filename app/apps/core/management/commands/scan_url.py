"""Ad-hoc real-site scrape check: `manage.py scan_url https://store.example`.

Runs the live fetch → extract → normalise pipeline against a single URL (or a
site's discovered catalogue) and prints what parsed. For manual validation
against real e-commerce sites — never used by the test suite.
"""
from django.core.management.base import BaseCommand

from apps.scanning.scraping.fetchers.http import HttpFetcher
from apps.scanning.scraping.orchestration import scrape_url


class Command(BaseCommand):
    help = "Fetch + extract a single product URL and print the normalised result."

    def add_arguments(self, parser):
        parser.add_argument("url")

    def handle(self, *args, **options):
        url = options["url"]
        fetcher = HttpFetcher()
        try:
            result, normalized = scrape_url(url, fetcher)
        finally:
            fetcher.close()
        self.stdout.write(f"HTTP {result.status_code} ok={result.ok} bytes={len(result.text)}")
        if normalized is None:
            self.stdout.write(self.style.WARNING("No product extracted (no JSON-LD/OG data found)."))
            return
        for field in ("title", "brand", "sku", "gtin", "price", "currency", "stock_status", "category"):
            self.stdout.write(f"  {field:14} {getattr(normalized, field)}")
