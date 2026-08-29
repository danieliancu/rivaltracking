from django.contrib import admin

from .models import (
    OwnCatalogueSource,
    OwnListing,
    OwnProduct,
    PriceSnapshot,
    Product,
    ProductListing,
    Promotion,
    StockSnapshot,
)


class ProductListingInline(admin.TabularInline):
    model = ProductListing
    extra = 0
    fields = ["competitor", "current_price", "current_stock_status", "is_primary", "active"]
    autocomplete_fields = ["competitor"]
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "category", "workspace"]
    list_filter = ["category", "workspace"]
    search_fields = ["name", "slug", "sku", "brand", "gtin", "ean", "mpn"]
    list_select_related = ["workspace"]
    autocomplete_fields = ["workspace"]
    inlines = [ProductListingInline]


@admin.register(ProductListing)
class ProductListingAdmin(admin.ModelAdmin):
    list_display = ["product", "competitor", "current_price", "current_stock_status", "is_primary", "active"]
    list_filter = ["current_stock_status", "is_primary", "active", "competitor"]
    search_fields = ["product__name", "competitor_sku", "source_url"]
    list_select_related = ["product", "competitor", "workspace"]
    autocomplete_fields = ["workspace", "product", "competitor"]


@admin.register(PriceSnapshot)
class PriceSnapshotAdmin(admin.ModelAdmin):
    list_display = ["listing", "price", "currency", "captured_at"]
    list_filter = ["currency"]
    list_select_related = ["listing", "listing__product"]
    date_hierarchy = "captured_at"


@admin.register(StockSnapshot)
class StockSnapshotAdmin(admin.ModelAdmin):
    list_display = ["listing", "stock_status", "quantity", "captured_at"]
    list_filter = ["stock_status"]
    list_select_related = ["listing", "listing__product"]
    date_hierarchy = "captured_at"


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ["title", "listing", "active", "started_at", "ended_at"]
    list_filter = ["active", "promotion_type"]
    list_select_related = ["listing", "listing__product"]


class OwnListingInline(admin.TabularInline):
    model = OwnListing
    extra = 0


@admin.register(OwnProduct)
class OwnProductAdmin(admin.ModelAdmin):
    list_display = ["name", "own_sku", "our_price", "rrp", "cost", "workspace"]
    search_fields = ["name", "own_sku"]
    list_select_related = ["workspace", "product"]
    autocomplete_fields = ["workspace", "product"]
    inlines = [OwnListingInline]


@admin.register(OwnCatalogueSource)
class OwnCatalogueSourceAdmin(admin.ModelAdmin):
    list_display = ["workspace", "source_type", "status", "website_url", "products_found", "last_import_at"]
    list_filter = ["source_type", "status", "workspace"]
    list_select_related = ["workspace"]
