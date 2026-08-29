"""Own-catalogue import runs on the `processing` queue."""
from celery import shared_task

from .models import OwnCatalogueSource


@shared_task(queue="processing")
def import_catalogue(source_id):
    from .importing import import_from_website

    source = OwnCatalogueSource.objects.filter(id=source_id).first()
    if source is None:
        return {"imported": False}
    if source.source_type == OwnCatalogueSource.SourceType.WEBSITE:
        import_from_website(source)
    return {"imported": True, "products": source.products_found, "status": source.status}
