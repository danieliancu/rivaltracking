"""Cross-app read helpers (port of prototype lib/format.ts paginate)."""

PAGE_SIZE = 8

RANGE_MINUTES = {"today": 1440, "7d": 10080, "30d": 43200}


def paginate(rows, page, page_size=PAGE_SIZE):
    """1-based slice with clamped page — mirrors paginate() in format.ts."""
    total = len(rows)
    page_count = max(1, -(-total // page_size))
    page = max(1, min(page, page_count))
    start = (page - 1) * page_size
    rows_slice = rows[start : start + page_size]
    return {
        "rows": rows_slice,
        "page": page,
        "page_count": page_count,
        "from": start + 1 if total else 0,
        "to": start + len(rows_slice),
        "total": total,
    }


def to_int(value, default=1):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
