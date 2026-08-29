"""Alert delivery channels. In-app always; email when configured.

Delivery is best-effort and isolated — a channel failure is recorded on the
alert and never propagates to change detection.
"""
from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail


def _recipients(alert):
    explicit = (alert.rule.config or {}).get("recipients") if alert.rule else None
    if explicit:
        return list(explicit)
    # Default: workspace members' emails.
    return list(
        alert.workspace.memberships.select_related("user").values_list(
            "user__email", flat=True
        )
    )


def _send_email(alert):
    recipients = [r for r in _recipients(alert) if r]
    if not recipients:
        return "skipped:no-recipients"
    send_mail(
        subject=f"[RivalTracking] {alert.title}",
        message=alert.message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )
    return "sent"


def deliver(alert):
    channels = (alert.rule.channels if alert.rule else None) or ["in_app"]
    results = {}
    for channel in channels:
        try:
            if channel == "email":
                results["email"] = _send_email(alert)
            else:
                results["in_app"] = "sent"  # the Alert row itself is the in-app delivery
        except Exception as exc:  # never let delivery break the pipeline
            results[channel] = f"failed:{str(exc)[:120]}"
    alert.delivery = results
    alert.save(update_fields=["delivery"])
    return results
