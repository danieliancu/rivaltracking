"""Mock data ported from prototype-react/src/lib/settings-data.ts — deterministic seed for Phase 1.

Section icons in SETTINGS_SECTIONS are ported from the sectionIcons map in
prototype-react/src/pages/settings.tsx.
"""

WORKSPACE_SETTINGS = {
    "name": "Acme Toys Ltd",
    "website": "https://acmetoys.co.uk",
    "market": "United Kingdom",
    "industry": "Toys & Games",
    "currency": "GBP (£)",
    "timezone": "Europe/London",
    "date_format": "DD/MM/YYYY",
}

WORKSPACE_OPTIONS = {
    "markets": ["United Kingdom", "United States", "Germany", "France", "Romania"],
    "industries": ["Toys & Games", "Fashion", "Electronics", "Home & Garden", "Beauty"],
    "currencies": ["GBP (£)", "EUR (€)", "USD ($)", "RON (lei)"],
    "timezones": ["Europe/London", "Europe/Bucharest", "Europe/Berlin", "America/New_York"],
    "date_formats": ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"],
}

MONITORING_SETTINGS = {
    "frequency": "Every 24 hours",
    "allow_overrides": True,
    "spread_scans": True,
    "scope": {
        "prices": True,
        "stock": True,
        "products": True,
        "promotions": True,
        "names": True,
        "categories": True,
    },
    "advanced_scope": {
        "descriptions": False,
        "review_counts": False,
        "badges": False,
        "images": False,
    },
    "ignore_threshold": "0",
    "confirm_removed": True,
    "status": {
        "competitors": "4",
        "interval": "24 hours",
        "last_activity": "12 min ago",
    },
}

MONITORING_SCOPE_LABELS = {
    "prices": "Track prices",
    "stock": "Track stock",
    "products": "Track new/removed products",
    "promotions": "Track promotions",
    "names": "Track product names",
    "categories": "Track categories",
    "descriptions": "Track descriptions",
    "review_counts": "Track review counts",
    "badges": "Track badges",
    "images": "Track images",
}

NOTIFICATION_SETTINGS = {
    "in_app": True,
    "priorities": {"high": True, "medium": True, "low": False},
    "email": True,
    "email_address": "user@company.com",
    "email_options": {
        "immediate_high": True,
        "daily_digest": True,
        "weekly_report": True,
        "monitoring_problems": True,
    },
    "digest_time": "08:00",
    "weekly_day": "Monday",
    "weekly_time": "08:00",
}

EMAIL_OPTION_LABELS = {
    "immediate_high": "Immediate high-priority alerts",
    "daily_digest": "Daily intelligence digest",
    "weekly_report": "Weekly intelligence report",
    "monitoring_problems": "Monitoring problems",
}

AI_SETTINGS = {
    "ai_analysis": True,
    "ai_in_reports": True,
    "ai_in_alerts": True,
    "style": "balanced",
    "show_evidence": True,
}

AI_STYLE_OPTIONS = [
    {"value": "concise", "label": "Concise", "hint": "Short key insights."},
    {"value": "balanced", "label": "Balanced", "hint": "Recommended default."},
    {"value": "detailed", "label": "Detailed", "hint": "More explanation and context."},
]

REPORT_SETTINGS = {
    "period": "Last 7 days",
    "competitors": "All monitored competitors",
    "ai_by_default": True,
    "branding_name": "Acme Toys Ltd",
    "detail": "standard",
    "daily_time": "08:00",
    "weekly_day": "Monday",
    "weekly_time": "08:00",
}

REPORT_DETAIL_OPTIONS = [
    {"value": "executive", "label": "Executive", "hint": "High-level summary only."},
    {"value": "standard", "label": "Standard", "hint": "Recommended default."},
    {"value": "detailed", "label": "Detailed", "hint": "Full data and breakdowns."},
]

TEAM_MEMBERS = [
    {"id": "m1", "name": "Daniel Iancu", "email": "daniel@acmetoys.co.uk", "role": "Owner", "status": "Active", "last_active": "Now"},
    {"id": "m2", "name": "Sarah Jones", "email": "sarah@acmetoys.co.uk", "role": "Analyst", "status": "Active", "last_active": "2h ago"},
    {"id": "m3", "name": "Alex Popescu", "email": "alex@acmetoys.co.uk", "role": "Viewer", "status": "Active", "last_active": "Yesterday"},
]

ROLE_DESCRIPTIONS = [
    {"role": "Owner", "description": "Full workspace access."},
    {"role": "Admin", "description": "Manage competitors, settings and users."},
    {"role": "Analyst", "description": "View intelligence, create reports/alerts, use Ask AI."},
    {"role": "Viewer", "description": "Read-only."},
]

DATA_SETTINGS = {
    "stats": [
        {"label": "Competitors", "value": "4"},
        {"label": "Products", "value": "8,746"},
        {"label": "Historical snapshots", "value": "Available"},
        {"label": "Monitoring since", "value": "10 August 2026"},
    ],
    "retention": "12 months",
    "retention_options": ["3 months", "12 months", "24 months"],
    "competitors": ["ToyWorld.co.uk", "PlayNest.co.uk", "HappyToyHouse.com", "LittleMindsToys.co.uk"],
}

BILLING = {
    "plan": "Growth",
    "status": "Active",
    "usage": [
        {"label": "Competitors", "used": 4, "limit": 10, "display": "4 / 10"},
        {"label": "Products monitored", "used": 8746, "limit": 25000, "display": "8,746 / 25,000"},
    ],
    "facts": [
        {"label": "Scan frequency", "value": "Every 12 hours"},
        {"label": "Historical data", "value": "12 months"},
    ],
}

SETTINGS_SECTIONS = [
    {"id": "workspace", "label": "Workspace", "icon": "building-2"},
    {"id": "monitoring", "label": "Monitoring", "icon": "radar"},
    {"id": "notifications", "label": "Notifications", "icon": "bell"},
    {"id": "ai", "label": "AI", "icon": "sparkles"},
    {"id": "reports", "label": "Reports", "icon": "file-bar-chart-2"},
    {"id": "team", "label": "Team", "icon": "users"},
    {"id": "data", "label": "Data & Privacy", "icon": "database"},
    {"id": "billing", "label": "Billing", "icon": "credit-card"},
]
