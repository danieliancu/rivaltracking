"""Discovery runs on the processing queue (beat or manual)."""
from celery import shared_task

from apps.accounts.models import Workspace

from . import engine


@shared_task(queue="processing")
def run_discovery_for_workspace(workspace_id):
    workspace = Workspace.objects.filter(id=workspace_id).first()
    if workspace is None:
        return {"suggested": 0}
    return {"suggested": engine.run_discovery(workspace)}
