from django.contrib import admin

from .models import Competitor


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ["name", "workspace", "status", "monitoring_enabled", "products_count", "last_scan_at"]
    list_filter = ["status", "monitoring_enabled", "workspace"]
    search_fields = ["name", "slug", "domain"]
    list_select_related = ["workspace"]
    autocomplete_fields = ["workspace"]
    readonly_fields = ["created_at", "updated_at"]
