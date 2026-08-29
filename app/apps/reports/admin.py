from django.contrib import admin

from .models import Report, ReportSchedule


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "status", "period", "generated_at", "workspace"]
    list_filter = ["status", "report_type", "workspace"]
    search_fields = ["title"]
    list_select_related = ["workspace", "generated_by"]


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "frequency", "run_time", "enabled", "next_run_at", "workspace"]
    list_filter = ["enabled", "workspace"]
    search_fields = ["name"]
    list_select_related = ["workspace"]
