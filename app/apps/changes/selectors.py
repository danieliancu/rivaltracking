"""Change-event reads over the mock store."""
from apps.core.mock.store import MockStore


def all_events(request):
    return MockStore(request).get("change_events")


def by_id(request, event_id):
    for event in all_events(request):
        if event["id"] == event_id:
            return event
    return None


def recent_for_competitor(request, competitor_name, kinds=None, limit=5):
    """dashboard/changes-table.tsx: latest events for one competitor."""
    rows = [
        e
        for e in all_events(request)
        if e["competitor"] == competitor_name and (not kinds or e["kind"] in kinds)
    ]
    return rows[:limit]
