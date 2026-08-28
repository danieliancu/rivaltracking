"""Global header search across competitors, products, and categories.

Mirrors the prototype header's client-side filter: name/SKU substring match,
capped at 4/5/4 results per group.
"""
from apps.core.entities import category_param
from apps.core.mock.store import MockStore


def global_search(request, query):
    q = query.strip().lower()
    if not q:
        return {"competitors": [], "products": [], "categories": []}

    store = MockStore(request)
    from apps.products.data import FILTER_OPTIONS

    competitors = [
        c for c in store.get("competitors") if q in c["name"].lower()
    ][:4]
    products = [
        p
        for p in store.get("products")
        if q in p["name"].lower() or q in p["sku"].lower()
    ][:5]
    categories = [
        {"name": c, "param": category_param(c)}
        for c in FILTER_OPTIONS["categories"]
        if c != "All categories" and q in c.lower()
    ][:4]
    return {"competitors": competitors, "products": products, "categories": categories}
