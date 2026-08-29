"""Token-authed catalogue ingestion API (seam)."""
import json

import pytest
from django.test import Client
from django.urls import reverse

from apps.catalogue import services
from apps.catalogue.models import OwnProduct

pytestmark = pytest.mark.django_db


def _post(token, products):
    return Client(HTTP_HOST="localhost").post(
        reverse("catalogue:api_ingest"),
        data=json.dumps({"products": products}),
        content_type="application/json",
        HTTP_X_API_TOKEN=token,
    )


def test_ingest_requires_valid_token(workspace):
    assert _post("", []).status_code == 401
    assert _post("nope", []).status_code == 401


def test_ingest_upserts_own_products(workspace):
    token = services.ensure_api_token(workspace)
    resp = _post(token, [
        {"sku": "API-1", "name": "Api Widget", "price": "12.99", "gtin": "5012345678900"},
        {"sku": "API-2", "name": "Api Gadget", "price": "7.50"},
    ])
    assert resp.status_code == 200
    body = resp.json()
    assert body["imported"] == 2
    own = OwnProduct.objects.get(workspace=workspace, own_sku="API-1")
    assert str(own.our_price) == "12.99"
    assert own.product is not None


def test_ingest_is_workspace_scoped_by_token(workspace, other_workspace):
    token = services.ensure_api_token(workspace)
    _post(token, [{"sku": "API-X", "name": "X"}])
    assert OwnProduct.objects.for_workspace(other_workspace).filter(own_sku="API-X").count() == 0
    assert OwnProduct.objects.for_workspace(workspace).filter(own_sku="API-X").count() == 1
