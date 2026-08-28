"""Ask AI template helpers.

`richtext` renders the **bold** markers used in canned bullets, mirroring the
RichText component in ask-ai/ai-response.tsx (font-bold text-foreground).
"""
import re

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


@register.filter
def richtext(value):
    escaped = conditional_escape(value or "")
    html = _BOLD_RE.sub(
        r'<strong class="font-bold text-foreground">\1</strong>', escaped
    )
    return mark_safe(html)
