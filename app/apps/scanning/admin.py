from django.contrib import admin

from .models import DiscoveredUrl, RawCapture, ScanJob


@admin.register(ScanJob)
class ScanJobAdmin(admin.ModelAdmin):
    list_display = ["id", "competitor", "status", "trigger_type", "changes_detected", "products_updated", "errors_count", "queued_at", "finished_at"]
    list_filter = ["status", "trigger_type", "workspace"]
    search_fields = ["competitor__name"]
    list_select_related = ["competitor", "workspace"]
    readonly_fields = ["queued_at", "started_at", "finished_at"]
    date_hierarchy = "queued_at"


@admin.register(DiscoveredUrl)
class DiscoveredUrlAdmin(admin.ModelAdmin):
    list_display = ["url", "competitor", "kind", "status", "fail_count", "last_seen_at"]
    list_filter = ["kind", "status", "workspace"]
    search_fields = ["url"]
    list_select_related = ["competitor", "workspace"]


@admin.register(RawCapture)
class RawCaptureAdmin(admin.ModelAdmin):
    list_display = ["url", "competitor", "http_status", "fetched_at", "retained_until"]
    list_filter = ["http_status", "workspace"]
    search_fields = ["url", "content_hash"]
    list_select_related = ["competitor", "workspace", "scan_job"]
    date_hierarchy = "fetched_at"
