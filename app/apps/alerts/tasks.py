"""Alert evaluation runs on the `alerts` queue after change detection."""
from celery import shared_task

from apps.changes.models import ChangeEvent

from . import engine
from .delivery import deliver


@shared_task(queue="alerts")
def evaluate_change_event(event_id):
    event = (
        ChangeEvent.objects.select_related("competitor", "product")
        .filter(id=event_id)
        .first()
    )
    if event is None:
        return {"alerts": 0}
    created = engine.evaluate_event(event)
    for alert in created:
        deliver(alert)
    return {"alerts": len(created)}
