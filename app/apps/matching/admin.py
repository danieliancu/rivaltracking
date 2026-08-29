from django.contrib import admin

from .models import MatchResult


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ["listing", "product", "confidence", "method", "status", "updated_at"]
    list_filter = ["status", "method", "workspace"]
    search_fields = ["listing__competitor_product_name", "product__name"]
    list_select_related = ["listing", "product", "workspace"]
