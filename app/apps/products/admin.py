from django.contrib import admin

from .models import WatchlistItem


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ["product", "workspace", "added_by", "created_at"]
    list_select_related = ["product", "workspace", "added_by"]
    search_fields = ["product__name"]
    autocomplete_fields = ["workspace", "product", "added_by"]
