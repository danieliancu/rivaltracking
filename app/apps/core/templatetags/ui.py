"""Shared UI component tags used across all page apps.

Variant-to-class maps live here (not in templates) so each component has a
single source of truth mirroring the prototype's shared/*.tsx components.
"""
import re
from functools import lru_cache
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from apps.core import format as fmt
from apps.core.entities import competitor_tone

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

    Inherits currentColor, so text-* utilities colour it exactly like the
    prototype's lucide-react components.
    """
    css = kwargs.get("class", "")
    svg = _icon_svg(name)
    svg = _CLASS_RE.sub(f'class="{css}"' if css else 'class=""', svg, count=1)
    return mark_safe(svg)


# ---------------------------------------------------------------------------
# Formatting filters

register.filter("gbp", fmt.gbp)
register.filter("rel_time", fmt.relative_time)


# ---------------------------------------------------------------------------
# KPI card — shared/kpi-card.tsx

KPI_TONES = {
    "info": "bg-info/10 text-info",
    "success": "bg-success/10 text-success",
    "danger": "bg-destructive/10 text-destructive",
    "warning": "bg-warning/10 text-warning",
    "purple": "bg-purple/10 text-purple",
    "teal": "bg-teal/10 text-teal",
}


@register.inclusion_tag("components/kpi_card.html")
def kpi_card(icon, tone, value, label, href=None):
    return {
        "icon": icon,
        "tone_class": KPI_TONES.get(tone, KPI_TONES["info"]),
        "value": value,
        "label": label,
        "href": href,
    }


# ---------------------------------------------------------------------------
# Badges — shared/status-badge.tsx, change-badge.tsx, stock-badge.tsx,
# impact-badge.tsx, alerts/alert-status-badge.tsx, reports/report-status-badge.tsx

BADGE_SHELL = (
    "inline-flex w-fit shrink-0 items-center justify-center gap-1.5 "
    "overflow-hidden whitespace-nowrap rounded-full border px-2 py-1 "
    "text-[11px] font-bold"
)

STATUS_VARIANTS = {
    "healthy": ("Healthy", "border-success/25 bg-success/10 text-success", "bg-success", False),
    "scanning": ("Scanning", "border-info/25 bg-info/10 text-info", "bg-info", True),
    "attention": ("Attention", "border-warning/25 bg-warning/10 text-warning", "bg-warning", False),
    "paused": ("Paused", "border-border bg-muted text-muted-foreground", "bg-muted-foreground", False),
    "initialising": ("Initialising", "border-purple/25 bg-purple/10 text-purple", "bg-purple", True),
    "blocked": ("Protected", "border-destructive/25 bg-destructive/10 text-destructive", "bg-destructive", False),
}


@register.inclusion_tag("components/status_badge.html")
def status_badge(status):
    label, classes, dot, pulse = STATUS_VARIANTS.get(status, STATUS_VARIANTS["healthy"])
    return {"shell": BADGE_SHELL, "label": label, "classes": classes, "dot": dot, "pulse": pulse}


CHANGE_VARIANTS = {
    "drop": ("trending-down", "border-success/25 bg-success/10 text-success"),
    "increase": ("trending-up", "border-destructive/25 bg-destructive/10 text-destructive"),
    "promo": ("badge-percent", "border-purple/25 bg-purple/10 text-purple"),
    "promo-end": ("badge-percent", "border-border bg-muted text-muted-foreground"),
    "oos": ("package-x", "border-warning/25 bg-warning/10 text-warning"),
    "back": ("package-check", "border-success/25 bg-success/10 text-success"),
    "new": ("sparkles", "border-info/25 bg-info/10 text-info"),
    "removed": ("trash-2", "border-destructive/25 bg-destructive/10 text-destructive"),
    "missing": ("circle-help", "border-warning/25 bg-warning/10 text-warning"),
    "name": ("pencil", "border-border bg-muted text-muted-foreground"),
    "category": ("folder-pen", "border-border bg-muted text-muted-foreground"),
    "description": ("file-text", "border-border bg-muted text-muted-foreground"),
    "variant-add": ("layers", "border-teal/25 bg-teal/10 text-teal"),
    "variant-remove": ("layers", "border-border bg-muted text-muted-foreground"),
}


@register.inclusion_tag("components/change_badge.html")
def change_badge(kind, label):
    icon_name, classes = CHANGE_VARIANTS.get(kind, CHANGE_VARIANTS["name"])
    return {"shell": BADGE_SHELL, "icon": icon_name, "classes": classes, "label": label}


@register.inclusion_tag("components/stock_badge.html")
def stock_badge(in_stock):
    if in_stock:
        classes, dot, label = "border-success/30 bg-success/10 text-success", "bg-success", "In stock"
    else:
        classes, dot, label = (
            "border-destructive/30 bg-destructive/10 text-destructive",
            "bg-destructive",
            "Out of stock",
        )
    return {"shell": BADGE_SHELL, "classes": classes, "dot": dot, "label": label}


IMPACT_VARIANTS = {
    "high": ("High", "border-warning/30 bg-warning/10 text-warning"),
    "medium": ("Medium", "border-info/25 bg-info/10 text-info"),
    "low": ("Low", "border-border bg-muted text-muted-foreground"),
}


@register.inclusion_tag("components/impact_badge.html")
def impact_badge(impact):
    label, classes = IMPACT_VARIANTS.get(impact, IMPACT_VARIANTS["low"])
    return {"shell": BADGE_SHELL, "label": label, "classes": classes}


# ---------------------------------------------------------------------------
# Change value (old → new) — shared/change-value.tsx

SECONDARY_TONES = {
    "success": "text-success",
    "destructive": "text-destructive",
    "purple": "text-purple",
    "muted": "text-muted-foreground",
}


@register.inclusion_tag("components/change_value.html")
def change_value(previous, current, secondary=None, secondary_tone="muted"):
    return {
        "previous": previous,
        "current": current,
        "secondary": secondary,
        "secondary_class": SECONDARY_TONES.get(secondary_tone, SECONDARY_TONES["muted"]),
    }


# ---------------------------------------------------------------------------
# Identities — shared/competitor-identity.tsx, product-identity.tsx

PRODUCT_TONES = {
    "info": "bg-info/10 text-info",
    "purple": "bg-purple/10 text-purple",
    "warning": "bg-warning/10 text-warning",
    "rose": "bg-rose/10 text-rose",
    "teal": "bg-teal/10 text-teal",
}

# products-table.tsx productIcons — slug → lucide glyph, fallback "package".
PRODUCT_ICONS = {
    "lego-castle-set": "blocks",
    "stem-robot-kit": "bot",
    "stem-coding-kit": "bot",
    "wooden-balance-bike": "bike",
    "unicorn-plush-xl": "rabbit",
    "personalised-puzzle": "puzzle",
    "garden-water-table": "waves",
    "baby-sensory-gym": "baby",
    "dinosaur-excavation-kit": "bone",
    "wooden-train-set": "train-front",
}


def product_icon_for(slug):
    return PRODUCT_ICONS.get(slug, "package")


@register.inclusion_tag("components/competitor_identity.html")
def competitor_identity(name, url=None):
    # Full literal class strings so the Tailwind scanner sees them.
    tone_classes = {
        "info": "bg-info/10 text-info",
        "purple": "bg-purple/10 text-purple",
        "teal": "bg-teal/10 text-teal",
        "warning": "bg-warning/10 text-warning",
        "rose": "bg-rose/10 text-rose",
    }
    return {"name": name, "url": url, "tone_class": tone_classes[competitor_tone(name)]}


@register.inclusion_tag("components/product_identity.html")
def product_identity(product=None, name=None, sku=None, tone=None, icon=None, href=None):
    """Accepts either a product/event-product dict or explicit fields."""
    if product:
        name = product.get("name")
        sku = sku if sku is not None else product.get("sku")
        tone = tone or product.get("tone")
        icon = icon or product.get("icon") or product_icon_for(product.get("slug", ""))
    return {
        "name": name,
        "sku": sku,
        "tone_class": PRODUCT_TONES.get(tone, PRODUCT_TONES["info"]),
        "icon": icon or "package",
        "href": href,
    }


# ---------------------------------------------------------------------------
# Product thumbnail (new in Phase 1 — the prototype has no product images)

THUMBNAIL_SIZES = {
    "sm": ("size-10", "size-4"),     # table cells
    "md": ("size-16", "size-5"),     # cards / drawers
    "lg": ("size-28", "size-7"),     # product detail header
}


@register.inclusion_tag("components/product_thumbnail.html")
def product_thumbnail(product, size="sm"):
    from django.templatetags.static import static

    box, glyph = THUMBNAIL_SIZES.get(size, THUMBNAIL_SIZES["sm"])
    image = product.get("image")
    if image and "://" not in image and not image.startswith("//"):
        # Local Phase-1 placeholder asset; scraped images are absolute URLs.
        image = static(image)
    return {
        "image": image,
        "name": product.get("name", ""),
        "tone_class": PRODUCT_TONES.get(product.get("tone"), PRODUCT_TONES["info"]),
        "icon": product.get("icon") or product_icon_for(product.get("slug", "")),
        "box_class": box,
        "glyph_class": glyph,
    }


@register.filter(name="discovery_tone")
def discovery_tone(candidate):
    from apps.discovery.selectors import tone_class

    return tone_class(candidate)


# ---------------------------------------------------------------------------
# Empty state — shared/empty-state.tsx

@register.inclusion_tag("components/empty_state.html")
def empty_state(heading, text, icon="search-x", action_label=None, action_href=None):
    return {
        "icon": icon,
        "heading": heading,
        "text": text,
        "action_label": action_label,
        "action_href": action_href,
    }


# ---------------------------------------------------------------------------
# Table pagination footer (PAGE_SIZE=8 tables; prev/next only)

@register.inclusion_tag("components/pagination.html", takes_context=True)
def pagination(context, page, noun):
    """`page` is a selectors.paginate() dict; links keep current filters."""
    params = context["request"].GET.copy()
    prev_params = params.copy()
    prev_params["page"] = page["page"] - 1
    next_params = params.copy()
    next_params["page"] = page["page"] + 1
    return {
        "page": page,
        "noun": noun,
        "prev_qs": prev_params.urlencode(),
        "next_qs": next_params.urlencode(),
    }


# ---------------------------------------------------------------------------
# Native filter select (confirmed decision: styled <select>)

@register.inclusion_tag("components/filter_select.html")
def filter_select(name, options, selected, width="w-fit", aria_label=None):
    """options: list of strings, {value,label} dicts, or
    {label, options: [...]} groups (rendered as <optgroup>)."""
    def norm(opt):
        if isinstance(opt, str):
            return {"value": opt, "label": opt}
        if "options" in opt:
            return {"label": opt["label"], "options": [norm(o) for o in opt["options"]]}
        return {"value": opt["value"], "label": opt.get("label", opt["value"])}

    return {
        "name": name,
        "options": [norm(o) for o in options],
        "selected": selected,
        "width": width,
        "aria_label": aria_label or name,
    }


# ---------------------------------------------------------------------------
# Chart mount — rendered by static/js/charts.js (Chart.js)

@register.inclusion_tag("components/chart.html")
def chart(chart_id, payload, height):
    return {"chart_id": chart_id, "payload": payload, "height": height}
