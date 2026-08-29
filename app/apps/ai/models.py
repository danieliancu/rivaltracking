"""AI persistence: conversations, messages and structured change analysis."""
from django.db import models

from apps.core.scoping import WorkspaceManager


class Conversation(models.Model):
    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="conversations"
    )
    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="conversations",
    )
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["workspace", "-updated_at"])]

    def __str__(self):
        return self.title


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        AI = "ai", "AI"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField(blank=True)
    # Citations / references to internal entities (product slugs, event ids…).
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"


class ChangeAnalysis(models.Model):
    class Urgency(models.TextChoices):
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    workspace = models.ForeignKey(
        "accounts.Workspace", on_delete=models.CASCADE, related_name="change_analyses"
    )
    change_event = models.OneToOneField(
        "changes.ChangeEvent", on_delete=models.CASCADE, related_name="analysis"
    )
    summary = models.TextField(blank=True)
    why_it_matters = models.TextField(blank=True)
    recommended_action = models.TextField(blank=True)
    confidence = models.FloatField(default=0.0)
    urgency = models.CharField(max_length=10, choices=Urgency.choices, default=Urgency.MEDIUM)
    supporting_points = models.JSONField(default=list, blank=True)
    provider = models.CharField(max_length=40, default="stub")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WorkspaceManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis of {self.change_event_id}"
