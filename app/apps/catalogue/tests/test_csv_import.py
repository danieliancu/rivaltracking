"""CSV own-catalogue import: mapping, upsert, validation, matching."""
import io
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.catalogue import csv_import
from apps.catalogue.models import OwnProduct

pytestmark = pytest.mark.django_db

CSV = b"sku,title,price,brand,gtin\nSKU1,My Widget,19.99,Acme,5011111111118\nSKU2,Other Thing,5.00,,\n"


def test_import_csv_upserts_and_matches(workspace):
    result = csv_import.import_csv(workspace, io.BytesIO(CSV))
    assert result["imported"] == 2
    assert "own_sku" in result["mapped"] and "our_price" in result["mapped"]
    own = OwnProduct.objects.get(workspace=workspace, own_sku="SKU1")
    assert own.our_price == Decimal("19.99")
    assert own.brand == "Acme"
    assert own.product is not None  # matched/created a canonical product


def test_import_csv_missing_columns_errors(workspace):
    result = csv_import.import_csv(workspace, io.BytesIO(b"colour,size\nred,large\n"))
    assert "error" in result


def test_csv_upload_view(client, workspace):
    upload = SimpleUploadedFile("products.csv", CSV, content_type="text/csv")
    response = client.post(reverse("settings_app:catalogue_csv"), {"file": upload})
    assert response.status_code == 200
    assert "Imported 2 new" in response.content.decode()
    assert OwnProduct.objects.filter(workspace=workspace).count() >= 2


def test_csv_import_is_isolated(workspace, other_workspace):
    csv_import.import_csv(workspace, io.BytesIO(CSV))
    assert OwnProduct.objects.for_workspace(other_workspace).filter(own_sku="SKU1").count() == 0
