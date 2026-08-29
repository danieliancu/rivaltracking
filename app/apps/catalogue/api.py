"""Token-authed catalogue ingestion endpoint (Phase 3.5 seam).

    POST /catalogue/api/ingest/
    Header: X-Api-Token: <workspace token>   (Settings → Connect catalogue → API)
    Body:   {"products": [{"sku","name","price","brand","gtin","ean","mpn","url"}...]}

Upserts into the same OwnProduct model as Website/CSV. Minimal by design.
"""
import json

from django.contrib.auth.decorators import login_not_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.models import WorkspaceSettings

from . import services


@csrf_exempt
@login_not_required
@require_POST
def ingest(request):
    token = request.headers.get("X-Api-Token", "").strip()
    settings_row = (
        WorkspaceSettings.objects.select_related("workspace").filter(api_token=token).first()
        if token
        else None
    )
    if settings_row is None:
        return JsonResponse({"error": "Invalid or missing API token."}, status=401)

    try:
        payload = json.loads(request.body or "{}")
    except ValueError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    workspace = settings_row.workspace
    imported, updated, errors = 0, 0, []
    for i, item in enumerate(payload.get("products", [])):
        own, note = services.upsert_own_product_dict(workspace, item)
        if own is None:
            errors.append({"index": i, "error": note})
        elif note == "updated":
            updated += 1
        else:
            imported += 1
    return JsonResponse({"imported": imported, "updated": updated, "errors": errors})
