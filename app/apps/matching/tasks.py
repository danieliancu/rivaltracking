"""Matching runs on the `matching` queue after a competitor scan."""
from celery import shared_task

from apps.competitors.models import Competitor

from . import engine


@shared_task(queue="matching")
def match_competitor_listings(competitor_id):
    competitor = Competitor.objects.filter(id=competitor_id).first()
    if competitor is None:
        return {"matched": 0}
    return {"matched": engine.match_competitor(competitor)}
