"""Report-specific template filters."""
from django import template

register = template.Library()


@register.filter(name="thousands")
def thousands(value):
    """Group an integer with commas — port of Number.toLocaleString()."""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return value
