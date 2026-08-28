"""Formatting helpers shared across apps.

The mock data stores times as canonical integer minutes-ago values
(mirroring the prototype's `*Minutes` fields); display strings are always
derived from them so sorting and filtering never drift from what is shown.
"""


def relative_time(minutes):
    """Render minutes-ago the way the prototype's fixture strings do."""
    if minutes is None:
        return "—"
    if minutes < 1:
        return "Just now"
    if minutes < 60:
        return f"{minutes} min ago"
    if minutes < 1440:
        hours = minutes // 60
        return f"{hours}h ago"
    days = minutes // 1440
    if days == 1:
        return "Yesterday"
    return f"{days}d ago"


def gbp(value):
    """£-formatted price. The prototype hard-codes GBP."""
    if value is None:
        return "—"
    return f"£{value:,.2f}"
