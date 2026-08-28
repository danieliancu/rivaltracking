"""Shared UI component tags used across all page apps."""
import re
from functools import lru_cache
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

ICON_DIR = Path(settings.BASE_DIR) / "static" / "icons" / "lucide"

_LICENSE_RE = re.compile(r"<!--.*?-->\s*", re.DOTALL)
_CLASS_RE = re.compile(r'class="[^"]*"')


@lru_cache(maxsize=None)
def _icon_svg(name):
    path = ICON_DIR / f"{name}.svg"
    if not path.is_file():
        raise template.TemplateSyntaxError(
            f'Unknown icon "{name}" — add the SVG to static/icons/lucide/.'
        )
    return _LICENSE_RE.sub("", path.read_text(encoding="utf-8")).strip()


@register.simple_tag(name="icon")
def icon(name, **kwargs):
    """Inline a lucide SVG: {% icon "store" class="size-4" %}.

    The SVG inherits currentColor, so text-* utilities colour it exactly like
    lucide-react components in the prototype.
    """
    css = kwargs.get("class", "")
    svg = _icon_svg(name)
    svg = _CLASS_RE.sub(f'class="{css}"' if css else 'class=""', svg, count=1)
    return mark_safe(svg)
