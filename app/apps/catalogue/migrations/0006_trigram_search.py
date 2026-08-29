"""Enable pg_trgm + GIN trigram indexes for fast catalogue search.

PostgreSQL only; a no-op on SQLite (local/tests) so the same migration set runs
everywhere.
"""
from django.db import migrations


def create_trigram(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    schema_editor.execute(
        "CREATE INDEX IF NOT EXISTS catalogue_product_name_trgm "
        "ON catalogue_product USING gin (name gin_trgm_ops)"
    )


def drop_trigram(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("DROP INDEX IF EXISTS catalogue_product_name_trgm")


class Migration(migrations.Migration):
    dependencies = [("catalogue", "0005_product_catalogue_p_workspa_9b7652_idx_and_more")]
    operations = [migrations.RunPython(create_trigram, drop_trigram)]
