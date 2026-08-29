from django.contrib import admin

from .models import DiscoveryCandidate


@admin.register(DiscoveryCandidate)
class DiscoveryCandidateAdmin(admin.ModelAdmin):
    list_display = ["name", "domain", "score", "cluster", "status", "workspace", "discovered_at"]
    list_filter = ["status", "cluster", "workspace"]
    search_fields = ["name", "domain"]
    list_select_related = ["workspace"]
