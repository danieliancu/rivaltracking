"""Canonical product layer.

Design goal: one canonical Product identity that can be matched to listings
from many competitors, plus the customer's own catalogue, so later phases can
compute price position, gaps and over/under-pricing.

    Product ── ProductListing ── Competitor        (competitor offers)
       └────── OwnProduct ────── OwnListing         (customer's own catalogue)

Automated matching is Phase 3; in Phase 2 the Product↔ProductListing links are
created by the seed / manual linkage only. Price and stock history live in
PriceSnapshot / StockSnapshot; the listing keeps a denormalised "current"
value for fast reads.
"""
from django.db import models

from apps.core.scoping import WorkspaceManager


class StockStatus(models.TextChoices):
    IN_STOCK = "in_stock", "In stock"
    OUT_OF_STOCK = "out_of_stock", "Out of stock"
    UNKNOWN = "unknown", "Unknown"


class Product(models.Model):
    """Canonical identity for an item, independent of any single competitor."""

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    brand = models.CharField(max_length=120, blank=True)
    model = models.CharField(max_length=120, blank=True)
    sku = models.CharField(max_length=80, blank=True)
    gtin = models.CharField(max_length=14, blank=True)
    ean = models.CharField(max_length=14, blank=True)
    upc = models.CharField(max_length=14, blank=True)
    mpn = models.CharField(max_length=80, blank=True)
    category = models.CharField(max_length=120, blank=True)
    image_url = models.CharField(max_length=300, blank=True)

    # Presentational identity (kept exact for the UI; deterministic otherwise).
    tone = models.CharField(max_length=20, blank=True)
    icon = models.CharField(max_length=40, blank=True)

    # Cross-competitor match quality. Real matching is Phase 3; seeded for now.
    match_confidence = models.PositiveIntegerField(null=True, blank=True)
    match_insight = models.CharField(max_length=400, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "slug"], name="unique_product_slug_per_workspace"
            )
        ]
        indexes = [
            models.Index(fields=["workspace", "category"]),
            models.Index(fields=["workspace", "gtin"]),
            models.Index(fields=["workspace", "sku"]),
        ]

    def __str__(self):
        return self.name


class ProductListing(models.Model):
    """A canonical Product as offered at a particular competitor."""

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="listings"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="listings"
    )
    competitor = models.ForeignKey(
        "competitors.Competitor", on_delete=models.CASCADE, related_name="listings"
    )
    source_url = models.CharField(max_length=500, blank=True)
    competitor_sku = models.CharField(max_length=80, blank=True)
    competitor_product_name = models.CharField(max_length=250, blank=True)

    current_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    previous_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    currency = models.CharField(max_length=3, default="GBP")
    current_stock_status = models.CharField(
        max_length=20, choices=StockStatus.choices, default=StockStatus.UNKNOWN
    )
    current_stock_quantity = models.PositiveIntegerField(null=True, blank=True)
    current_promotion = models.CharField(max_length=200, blank=True)

    # The listing that represents the product in the flat products table.
    is_primary = models.BooleanField(default=False)

    # Denormalised "latest change" indicator shown on the product row.
    change_kind = models.CharField(max_length=20, blank=True)
    change_label = models.CharField(max_length=60, blank=True)
    last_change_at = models.DateTimeField(null=True, blank=True)

    first_seen_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    # Consecutive scans in which this listing was not seen; a removal event is
    # only emitted once it crosses LISTING_MISSES_BEFORE_REMOVED (avoids false
    # removals from transient crawl failures).
    consecutive_misses = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-last_change_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "competitor", "source_url"],
                condition=~models.Q(source_url=""),
                name="unique_listing_source_url",
            )
        ]
        indexes = [
            models.Index(fields=["workspace", "competitor"]),
            models.Index(fields=["product"]),
            models.Index(fields=["workspace", "active"]),
        ]

    def __str__(self):
        return f"{self.product} @ {self.competitor}"

    @property
    def in_stock(self):
        return self.current_stock_status == StockStatus.IN_STOCK


class OwnProduct(models.Model):
    """A product in the customer's own catalogue, optionally matched to a Product."""

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="own_products"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="own_products",
    )
    name = models.CharField(max_length=200)
    own_sku = models.CharField(max_length=80)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    our_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    currency = models.CharField(max_length=3, default="GBP")
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "own_sku"], name="unique_own_sku_per_workspace"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.own_sku})"


class OwnListing(models.Model):
    """A sales channel for an OwnProduct (own website, marketplace, …)."""

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="own_listings"
    )
    own_product = models.ForeignKey(
        OwnProduct, on_delete=models.CASCADE, related_name="listings"
    )
    channel = models.CharField(max_length=80)
    url = models.CharField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="GBP")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["channel"]

    def __str__(self):
        return f"{self.own_product} · {self.channel}"


class PriceSnapshot(models.Model):
    """A price observed for a listing at a point in time (history / charts)."""

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="price_snapshots"
    )
    listing = models.ForeignKey(
        ProductListing, on_delete=models.CASCADE, related_name="price_snapshots"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="GBP")
    captured_at = models.DateTimeField()

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-captured_at"]
        indexes = [
            models.Index(fields=["listing", "-captured_at"]),
            models.Index(fields=["workspace", "-captured_at"]),
        ]

    def __str__(self):
        return f"{self.listing} {self.price} @ {self.captured_at:%Y-%m-%d}"


class StockSnapshot(models.Model):
    """A stock status observed for a listing at a point in time."""

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="stock_snapshots"
    )
    listing = models.ForeignKey(
        ProductListing, on_delete=models.CASCADE, related_name="stock_snapshots"
    )
    stock_status = models.CharField(max_length=20, choices=StockStatus.choices)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    captured_at = models.DateTimeField()

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-captured_at"]
        indexes = [
            models.Index(fields=["listing", "-captured_at"]),
            models.Index(fields=["workspace", "-captured_at"]),
        ]

    def __str__(self):
        return f"{self.listing} {self.stock_status} @ {self.captured_at:%Y-%m-%d}"


class Promotion(models.Model):
    """A promotion detected on a listing. Kept flexible for messy real data."""

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="promotions"
    )
    listing = models.ForeignKey(
        ProductListing, on_delete=models.CASCADE, related_name="promotions"
    )
    title = models.CharField(max_length=200, blank=True)
    promotion_type = models.CharField(max_length=60, blank=True)
    value = models.CharField(max_length=60, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    captured_at = models.DateTimeField()

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-captured_at"]
        indexes = [
            models.Index(fields=["listing", "active"]),
            models.Index(fields=["workspace", "-captured_at"]),
        ]

    def __str__(self):
        return self.title or f"Promotion on {self.listing}"
