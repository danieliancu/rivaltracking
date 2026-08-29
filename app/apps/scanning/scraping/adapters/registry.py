"""Pick the most specific adapter for a fetched page (generic is the fallback)."""
from .generic import GenericAdapter
from .shopify import ShopifyAdapter
from .woocommerce import WooCommerceAdapter

# Order matters: most specific first, generic last.
ADAPTERS = [ShopifyAdapter, WooCommerceAdapter, GenericAdapter]


def select_adapter(fetch_result):
    for adapter_cls in ADAPTERS:
        if adapter_cls.detect(fetch_result):
            return adapter_cls()
    return GenericAdapter()
