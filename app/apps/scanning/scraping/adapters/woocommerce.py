"""WooCommerce adapter: detects WooCommerce (WordPress) stores. Uses the
default JSON-LD/DOM extraction pipeline."""
from .base import Adapter


class WooCommerceAdapter(Adapter):
    name = "woocommerce"

    @staticmethod
    def detect(fetch_result) -> bool:
        text = fetch_result.text or ""
        return (
            "woocommerce" in text.lower()
            or "wp-content/plugins/woocommerce" in text
            or 'class="woocommerce' in text
        )
