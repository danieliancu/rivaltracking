"""Product image handling — storage abstraction (S3-ready) + thumbnail seam.

Scaffold for Phase 3: the interface and a pass-through store are in place so the
UI never hotlinks unstable originals once the fetch/resize worker is enabled.
Real fetch → hash-dedupe → resize → object-storage wiring is deferred; the
`{% product_thumbnail %}` component already renders a source URL or an icon
fallback, so nothing breaks in the meantime.
"""
from __future__ import annotations

import hashlib


class ImageStore:
    """Storage backend interface (a FileSystem/S3 implementation slots in here)."""

    def key_for(self, source_url: str) -> str:
        return hashlib.sha256(source_url.encode("utf-8", "ignore")).hexdigest()[:32]

    def store(self, source_url: str, data: bytes, content_type: str) -> str:  # pragma: no cover - scaffold
        raise NotImplementedError

    def url_for(self, key: str) -> str:  # pragma: no cover - scaffold
        raise NotImplementedError


class PassthroughImageStore(ImageStore):
    """Default: serve the source URL directly (no fetching/resizing yet)."""

    def url_for(self, key: str) -> str:
        return ""


def get_image_store() -> ImageStore:
    return PassthroughImageStore()


def thumbnail_url(product):
    """The URL the UI should use for a product thumbnail.

    Today this is the stored source image; when the thumbnail worker is enabled
    it becomes the cached, resized, deduplicated object-storage URL.
    """
    return getattr(product, "image_url", "") or ""
