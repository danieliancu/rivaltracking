from django.contrib import admin

from .models import ChangeEvent


@admin.register(ChangeEvent)
class ChangeEventAdmin(admin.ModelAdmin):
    list_display = ["label", "event_type", "impact", "competitor", "product", "detected_at"]
    list_filter = ["event_type", "impact", "competitor", "workspace"]
    search_fields = ["label", "product__name", "competitor__name"]
    list_select_related = ["competitor", "product", "workspace"]
    autocomplete_fields = ["workspace", "competitor", "product", "listing"]
    date_hierarchy = "detected_at"
