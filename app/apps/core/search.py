"""Global header search across competitors, products and categories (ORM).

Mirrors the prototype header's client-side filter: name/SKU substring match,
capped at 4/5/4 results per group, scoped to the current workspace.
"""
from django.db import connection
from django.db.models import Q

from apps.catalogue.models import Product
from apps.competitors.models import Competitor
from apps.core.entities import category_param


def _product_search(workspace, q):
    """Trigram-ranked search on PostgreSQL; icontains elsewhere.

    Searches product name, SKU and GTIN/EAN so real catalogues are findable.
    """
    base = Product.objects.for_workspace(workspace).filter(
        Q(name__icontains=q) | Q(sku__icontains=q) | Q(gtin__icontains=q) | Q(ean__icontains=q)
    )
    if connection.vendor == "postgresql":
        from django.contrib.postgres.search import TrigramSimilarity

        base = base.annotate(rank=TrigramSimilarity("name", q)).order_by("-rank")
    return list(base.values("name", "slug", "sku")[:5])


def global_search(request, query):
    q = query.strip()
    if not q:
        return {"competitors": [], "products": [], "categories": []}

    workspace = getattr(request, "workspace", None)

    competitors = list(
        Competitor.objects.for_workspace(workspace)
        .filter(Q(name__icontains=q) | Q(domain__icontains=q))
        .values("name", "slug")[:4]
    )
    products = _product_search(workspace, q)
    category_names = (
        Product.objects.for_workspace(workspace)
        .filter(category__icontains=q)
        .order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )
    categories = [
        {"name": name, "param": category_param(name)}
        for name in list(category_names)[:4]
    ]
    return {"competitors": competitors, "products": products, "categories": categories}
