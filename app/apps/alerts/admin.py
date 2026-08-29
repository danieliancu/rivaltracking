from django.contrib import admin

from .models import Alert, AlertRule


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ["name", "type_group", "competitors", "enabled", "priority", "last_triggered_at"]
    list_filter = ["type_group", "enabled", "priority", "workspace"]
    search_fields = ["name", "condition"]
    list_select_related = ["workspace", "created_by"]


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ["title", "rule", "status", "triggered_at"]
    list_filter = ["status", "workspace"]
    search_fields = ["title", "message"]
    list_select_related = ["rule", "workspace", "change_event"]
    date_hierarchy = "triggered_at"
