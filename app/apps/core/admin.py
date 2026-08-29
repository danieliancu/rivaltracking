from django.contrib import admin

from .models import WorkspaceDemoState


@admin.register(WorkspaceDemoState)
class WorkspaceDemoStateAdmin(admin.ModelAdmin):
    list_display = ["workspace", "updated_at"]
    list_select_related = ["workspace"]
    search_fields = ["workspace__name"]
