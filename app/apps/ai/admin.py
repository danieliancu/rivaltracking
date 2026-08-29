from django.contrib import admin

from .models import ChangeAnalysis, Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["title", "workspace", "user", "updated_at"]
    list_filter = ["workspace"]
    search_fields = ["title"]
    list_select_related = ["workspace", "user"]
    inlines = [MessageInline]


@admin.register(ChangeAnalysis)
class ChangeAnalysisAdmin(admin.ModelAdmin):
    list_display = ["change_event", "urgency", "confidence", "provider", "created_at"]
    list_filter = ["urgency", "provider", "workspace"]
    list_select_related = ["change_event", "workspace"]
