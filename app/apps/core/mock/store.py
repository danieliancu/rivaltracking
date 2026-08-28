"""Session-backed copy-on-write store over the deterministic seed data.

Reads fall through to the immutable module-level seeds until a collection is
first mutated, at which point that collection (only) is deep-copied into the
session. This gives every browser its own mutable demo workspace that can be
reset at any time, without any global state that autoreload would wipe.

Views never touch this directly — selectors read, services mutate.
"""
from copy import deepcopy

SESSION_KEY = "mock"


def _seeds():
    # Imported lazily so data modules can be developed independently.
    from apps.alerts import data as alerts
    from apps.ai import data as ai
    from apps.competitors import data as competitors
    from apps.discovery import data as discovery
    from apps.products import data as products
    from apps.changes import data as changes
    from apps.reports import data as reports
    from apps.settings_app import data as settings_app

    return {
        "competitors": competitors.COMPETITOR_ROWS,
        "products": products.PRODUCTS,
        "change_events": changes.CHANGE_EVENTS,
        "discovery_candidates": discovery.DISCOVERY_CANDIDATES_SEED,
        "alert_rules": alerts.ALERT_RULES,
        "recent_alerts": alerts.RECENT_ALERTS,
        "reports": reports.GENERATED_REPORTS,
        "report_schedules": reports.REPORT_SCHEDULES,
        "conversations": ai.CONVERSATION_HISTORY,
        "watchlist": [],
        "competitor_configs": {},
        "settings": {
            "workspace": settings_app.WORKSPACE_SETTINGS,
            "monitoring": settings_app.MONITORING_SETTINGS,
            "notifications": settings_app.NOTIFICATION_SETTINGS,
            "ai": settings_app.AI_SETTINGS,
            "reports": settings_app.REPORT_SETTINGS,
            "team": settings_app.TEAM_MEMBERS,
        },
    }


class MockStore:
    def __init__(self, request):
        self.request = request

    def get(self, name):
        """Read a collection. Treat the result as immutable."""
        session_data = self.request.session.get(SESSION_KEY)
        if session_data is not None and name in session_data:
            return session_data[name]
        return _seeds()[name]

    def mutate(self, name, fn):
        """Apply fn to the session's own copy of a collection and persist."""
        session_data = self.request.session.setdefault(SESSION_KEY, {})
        if name not in session_data:
            session_data[name] = deepcopy(_seeds()[name])
        result = fn(session_data[name])
        self.request.session.modified = True
        return result

    def replace(self, name, value):
        """Replace a collection wholesale (e.g. filtered deletions)."""
        session_data = self.request.session.setdefault(SESSION_KEY, {})
        session_data[name] = value
        self.request.session.modified = True

    def reset(self):
        self.request.session.pop(SESSION_KEY, None)
