"""AI tasks (ai queue). AI runs only on structured events, never raw pages, and
a failure here never rolls back detected changes."""
import re

from celery import shared_task

from apps.catalogue.models import OwnProduct
from apps.changes.models import ChangeEvent
from apps.changes.significance import is_ai_eligible

from .models import ChangeAnalysis
from .providers import get_provider


def _pct(secondary):
    if not secondary:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", secondary)
    return float(m.group()) if m else None


def _event_payload(event):
    our_price = None
    if event.product_id:
        own = OwnProduct.objects.filter(
            workspace=event.workspace, product_id=event.product_id
        ).exclude(our_price=None).first()
        if own:
            our_price = float(own.our_price)
    return {
        "event_type": event.event_type,
        "product": event.product.name if event.product else "",
        "competitor": event.competitor.name,
        "old_price": event.previous_value,
        "new_price": event.new_value,
        "change_percent": _pct(event.secondary),
        "our_price": our_price,
        "impact": event.impact,
    }


@shared_task(queue="ai")
def analyse_change(event_id):
    event = (
        ChangeEvent.objects.select_related("product", "competitor")
        .filter(id=event_id)
        .first()
    )
    if event is None or not is_ai_eligible(event):
        return {"analysed": False}
    provider = get_provider()
    insight = provider.analyse_change(_event_payload(event))
    ChangeAnalysis.objects.update_or_create(
        change_event=event,
        defaults={
            "workspace": event.workspace,
            "summary": insight.summary,
            "why_it_matters": insight.why_it_matters,
            "recommended_action": insight.recommended_action,
            "confidence": insight.confidence,
            "urgency": insight.urgency,
            "supporting_points": insight.supporting_points,
            "provider": provider.name,
        },
    )
    return {"analysed": True, "event_id": event_id}
