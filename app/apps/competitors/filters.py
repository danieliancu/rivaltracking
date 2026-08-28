"""Pure filter/sort for the Monitored Competitors table.

Port of the useMemo in components/competitors/competitors-table.tsx.
"""
from urllib.parse import urlencode

# competitors-table.tsx: Filter and Sort unions.
STATUS_FILTERS = ["all", "healthy", "attention", "scanning"]
SORT_LABELS = {
    "activity": "Most activity",
    "recent": "Recently added",
    "products": "Most products",
    "scanned": "Last scanned",
}

DEFAULT_STATUS = "all"
DEFAULT_SORT = "activity"

# Number.MAX_SAFE_INTEGER — pushes never-scanned rows last for the "scanned" sort.
_MAX_MINUTES = 9007199254740991


def filters_from_params(params):
    """URL params → the table's filter state (invalid values fall back)."""
    q = (params.get("q") or "").strip()
    status = params.get("status") or DEFAULT_STATUS
    if status not in STATUS_FILTERS:
        status = DEFAULT_STATUS
    sort = params.get("sort") or DEFAULT_SORT
    if sort not in SORT_LABELS:
        sort = DEFAULT_SORT
    return {"q": q, "status": status, "sort": sort}


def filter_rows(rows, f):
    query = f["q"].lower()
    out = [r for r in rows if query in r["name"].lower()]
    if f["status"] != "all":
        out = [r for r in out if r["status"] == f["status"]]
    return out


def sort_rows(rows, sort):
    """Stable sort mirroring the tsx comparators (Python sort is stable)."""
    if sort == "recent":
        return sorted(rows, key=lambda r: r["added_at"], reverse=True)
    if sort == "products":
        return sorted(
            rows, key=lambda r: r["products"] if r["products"] is not None else -1, reverse=True
        )
    if sort == "scanned":
        return sorted(
            rows,
            key=lambda r: r["last_scan_minutes"]
            if r["last_scan_minutes"] is not None
            else _MAX_MINUTES,
        )
    # "activity" (default)
    return sorted(
        rows,
        key=lambda r: r["changes_today"] if r["changes_today"] is not None else -1,
        reverse=True,
    )


def canonical_query(f):
    """Querystring with defaults omitted (drives HX-Push-Url)."""
    parts = []
    if f["q"]:
        parts.append(("q", f["q"]))
    if f["status"] != DEFAULT_STATUS:
        parts.append(("status", f["status"]))
    if f["sort"] != DEFAULT_SORT:
        parts.append(("sort", f["sort"]))
    return urlencode(parts)
