"""Slug and identity helpers ported from prototype-react/src/lib/entities.ts."""
import re


def slugify(value):
    """ToyWorld.co.uk or https://www.toyworld.co.uk/x -> toyworld-co-uk."""
    value = re.sub(r"^https?://", "", value.strip().lower())
    value = re.sub(r"^www\.", "", value)
    value = value.split("/")[0]
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def category_param(name):
    """Category display name -> URL token (Outdoor Toys -> outdoor-toys)."""
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def category_from_param(param, categories):
    for name in categories:
        if category_param(name) == param:
            return name
    return None


# Deterministic tone for competitor identity tiles. Reproduces the exact
# 32-bit signed `(hash * 31 + charCode) | 0` + Math.abs() algorithm from
# shared/competitor-identity.tsx so colours match the prototype per name.
COMPETITOR_TONES = ["info", "purple", "teal", "warning", "rose"]


def competitor_tone(name):
    value = 0
    for ch in name:
        value = (value * 31 + ord(ch)) & 0xFFFFFFFF  # congruent to JS |0 mod 2^32
    if value >= 0x80000000:  # reinterpret as 32-bit signed, as JS does
        value -= 0x100000000
    return COMPETITOR_TONES[abs(value) % len(COMPETITOR_TONES)]
