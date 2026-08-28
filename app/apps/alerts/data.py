"""Mock data ported from prototype-react/src/lib/alerts-data.ts — deterministic seed for Phase 1.

KIND_TO_TRIGGER is ported from prototype-react/src/pages/alerts.tsx.
"""

TYPE_GROUP_META = {
    "price": {"label": "Price", "icon": "tags", "tone": "bg-success/10 text-success"},
    "stock": {"label": "Stock", "icon": "package-x", "tone": "bg-warning/10 text-warning"},
    "products": {"label": "Products", "icon": "package", "tone": "bg-info/10 text-info"},
    "promotions": {"label": "Promotions", "icon": "badge-percent", "tone": "bg-purple/10 text-purple"},
    "patterns": {"label": "Patterns", "icon": "activity", "tone": "bg-teal/10 text-teal"},
}

ALERT_RULES = [
    {
        "id": "toyworld-drops",
        "name": "Large ToyWorld price drops",
        "type_group": "price",
        "condition": "Price decreases by more than 10%",
        "competitors": "ToyWorld.co.uk",
        "frequency": "Immediate",
        "last_triggered": "12 min ago",
        "last_triggered_minutes": 12,
        "active": True,
        "priority": "high",
        "created_at": "2026-06-02",
    },
    {
        "id": "outdoor-stockouts",
        "name": "Outdoor Toys stock-outs",
        "type_group": "stock",
        "condition": "Product goes out of stock",
        "competitors": "All competitors",
        "category": "Outdoor Toys",
        "frequency": "Immediate",
        "last_triggered": "2h ago",
        "last_triggered_minutes": 120,
        "active": True,
        "priority": "medium",
        "created_at": "2026-06-18",
    },
    {
        "id": "new-educational",
        "name": "New Educational Toys",
        "type_group": "products",
        "condition": "New product detected",
        "competitors": "All competitors",
        "category": "Educational Toys",
        "frequency": "Daily summary",
        "last_triggered": "Today, 08:00",
        "last_triggered_minutes": 400,
        "active": True,
        "created_at": "2026-07-01",
    },
    {
        "id": "toyworld-promos",
        "name": "ToyWorld promotions",
        "type_group": "promotions",
        "condition": "Promotion starts",
        "competitors": "ToyWorld.co.uk",
        "frequency": "Immediate",
        "last_triggered": "Yesterday",
        "last_triggered_minutes": 1440,
        "active": True,
        "created_at": "2026-07-14",
    },
    {
        "id": "major-campaign",
        "name": "Major competitor campaign",
        "type_group": "patterns",
        "condition": "20+ related price changes within 6 hours",
        "competitors": "All competitors",
        "frequency": "Immediate",
        "last_triggered": "3h ago",
        "last_triggered_minutes": 180,
        "active": True,
        "priority": "high",
        "pattern_based": True,
        "created_at": "2026-07-22",
    },
    {
        "id": "playnest-increases",
        "name": "PlayNest price increases",
        "type_group": "price",
        "condition": "Price increases by more than 5%",
        "competitors": "PlayNest.co.uk",
        "frequency": "Hourly summary",
        "last_triggered": "3 days ago",
        "last_triggered_minutes": 4320,
        "active": False,
        "created_at": "2026-08-02",
    },
]

RECENT_ALERTS = [
    {
        "id": 5531,
        "rule_id": "toyworld-drops",
        "rule_name": "Large ToyWorld price drops",
        "event": "Price decreased 16.7%",
        "kind": "drop",
        "competitor": "ToyWorld.co.uk",
        "product": "LEGO Castle Set",
        "product_slug": "lego-castle-set",
        "priority": "high",
        "triggered": "12 min ago",
        "detected_at": "25 Aug, 14:32",
        "status": "new",
        "rule": {
            "scope": "ToyWorld.co.uk",
            "condition": "Price decrease > 10%",
            "detected": "-16.67%",
        },
        "evidence": {
            "previous": "£59.99",
            "current": "£49.99",
            "difference": "-£10.00",
            "change": "-16.67%",
            "stock": "In stock",
            "category": "Construction Toys",
        },
        "ai_note": "This price reduction is part of a broader pricing movement. ToyWorld has reduced 42 products across Outdoor Toys and Construction Toys during the last six hours.",
    },
    {
        "id": 5530,
        "rule_id": "major-campaign",
        "rule_name": "Major competitor campaign",
        "event": "42 related price reductions",
        "kind": "drop",
        "competitor": "ToyWorld.co.uk",
        "pattern_label": "42 related price reductions",
        "is_pattern": True,
        "category": "Outdoor Toys",
        "priority": "high",
        "triggered": "3h ago",
        "detected_at": "25 Aug, 11:05",
        "status": "new",
        "rule": {
            "scope": "All competitors",
            "condition": "20+ related price changes within 6 hours",
            "detected": "42 related changes in 5h 40m",
        },
        "ai_note": "The scale and timing of these reductions suggest a coordinated Outdoor Toys campaign rather than isolated adjustments.",
    },
    {
        "id": 5529,
        "rule_id": "new-educational",
        "rule_name": "New Educational Toys",
        "event": "5 new products detected",
        "kind": "new",
        "competitor": "PlayNest.co.uk",
        "pattern_label": "5 new products detected",
        "is_pattern": True,
        "category": "Educational Toys",
        "priority": "medium",
        "triggered": "Today, 08:00",
        "detected_at": "25 Aug, 08:00",
        "status": "new",
        "rule": {
            "scope": "All competitors · Educational Toys",
            "condition": "New product detected (daily summary)",
            "detected": "5 new products since yesterday",
        },
        "ai_note": "PlayNest continues to expand Educational Toys — 24 products added this week, concentrated in STEM and coding kits.",
    },
    {
        "id": 5528,
        "rule_id": "outdoor-stockouts",
        "rule_name": "Outdoor Toys stock-outs",
        "event": "Out of stock",
        "kind": "oos",
        "competitor": "ToyWorld.co.uk",
        "product": "Wooden Balance Bike",
        "product_slug": "wooden-balance-bike",
        "priority": "medium",
        "triggered": "2h ago",
        "detected_at": "25 Aug, 12:14",
        "status": "viewed",
        "rule": {
            "scope": "All competitors · Outdoor Toys",
            "condition": "Product goes out of stock",
            "detected": "Stock changed: In stock → Out of stock",
        },
        "evidence": {
            "previous": "In stock",
            "current": "Out of stock",
            "difference": "—",
            "change": "Stock status",
            "stock": "Out of stock",
            "category": "Outdoor Toys",
        },
        "ai_note": "Outdoor Toys stock-outs at ToyWorld coincide with their discount campaign — demand may be depleting discounted lines.",
    },
    {
        "id": 5527,
        "rule_id": "outdoor-stockouts",
        "rule_name": "Outdoor Toys stock-outs",
        "event": "Back in stock",
        "kind": "back",
        "competitor": "LittleMindsToys.co.uk",
        "product": "STEM Coding Kit",
        "product_slug": "stem-coding-kit",
        "priority": "low",
        "triggered": "10h ago",
        "detected_at": "25 Aug, 03:18",
        "status": "new",
        "rule": {
            "scope": "All competitors · Outdoor Toys",
            "condition": "Stock status changes",
            "detected": "Stock changed: Out of stock → In stock",
        },
        "evidence": {
            "previous": "Out of stock",
            "current": "In stock",
            "difference": "—",
            "change": "Stock status",
            "stock": "In stock",
            "category": "Educational Toys",
        },
        "ai_note": "This product returned after 9 days out of stock. Restocks in Educational Toys often precede promotional pushes.",
    },
    {
        "id": 5526,
        "rule_id": "toyworld-promos",
        "rule_name": "ToyWorld promotions",
        "event": "Promotion started: 20% off",
        "kind": "promo",
        "competitor": "ToyWorld.co.uk",
        "product": "STEM Robot Kit",
        "product_slug": "stem-robot-kit",
        "priority": "medium",
        "triggered": "Yesterday",
        "detected_at": "24 Aug, 10:36",
        "status": "new",
        "rule": {
            "scope": "ToyWorld.co.uk",
            "condition": "Promotion starts",
            "detected": "New promotion: 20% off",
        },
        "evidence": {
            "previous": "No promotion",
            "current": "20% off",
            "difference": "—",
            "change": "Promotion",
            "stock": "In stock",
            "category": "Educational Toys",
        },
        "ai_note": "ToyWorld started 5 promotions in Educational Toys this week — likely part of a wider seasonal campaign.",
    },
]

ALERT_KPIS = [
    {"id": "active", "label": "Active alerts", "value": "8", "tone": "info"},
    {"id": "triggered", "label": "Triggered today", "value": "14", "tone": "purple"},
    {"id": "high", "label": "High priority", "value": "3", "tone": "warning"},
    {"id": "covered", "label": "Competitors covered", "value": "4", "tone": "teal"},
]

ALERT_ACTIVITY = {
    "Today": [
        {"label": "00:00", "price": 0, "stock": 0, "product": 0, "promotions": 0},
        {"label": "04:00", "price": 1, "stock": 1, "product": 0, "promotions": 0},
        {"label": "08:00", "price": 2, "stock": 0, "product": 1, "promotions": 0},
        {"label": "12:00", "price": 5, "stock": 1, "product": 1, "promotions": 1},
        {"label": "16:00", "price": 1, "stock": 0, "product": 0, "promotions": 0},
        {"label": "20:00", "price": 0, "stock": 0, "product": 0, "promotions": 0},
    ],
    "7D": [
        {"label": "19 Aug", "price": 3, "stock": 2, "product": 1, "promotions": 0},
        {"label": "20 Aug", "price": 4, "stock": 1, "product": 2, "promotions": 1},
        {"label": "21 Aug", "price": 2, "stock": 3, "product": 1, "promotions": 0},
        {"label": "22 Aug", "price": 9, "stock": 2, "product": 2, "promotions": 1},
        {"label": "23 Aug", "price": 7, "stock": 1, "product": 3, "promotions": 0},
        {"label": "24 Aug", "price": 5, "stock": 2, "product": 1, "promotions": 2},
        {"label": "25 Aug", "price": 9, "stock": 2, "product": 2, "promotions": 1},
    ],
    "30D": [
        {"label": "Week 31", "price": 14, "stock": 8, "product": 6, "promotions": 3},
        {"label": "Week 32", "price": 18, "stock": 11, "product": 9, "promotions": 4},
        {"label": "Week 33", "price": 12, "stock": 7, "product": 11, "promotions": 2},
        {"label": "Week 34", "price": 39, "stock": 12, "product": 12, "promotions": 5},
    ],
}

MOST_TRIGGERED_RULES = [
    {"name": "Large ToyWorld price drops", "count": 18},
    {"name": "Outdoor stock-outs", "count": 11},
    {"name": "New Educational Toys", "count": 7},
    {"name": "Promotion started", "count": 5},
]

ALERT_COVERAGE = [
    {"label": "Active rules", "value": "8"},
    {"label": "Competitors covered", "value": "4"},
    {"label": "Categories monitored", "value": "6"},
    {"label": "High-priority rules", "value": "3"},
]

# Step 1 trigger catalog — business language only, no event-type codes.
ALERT_TRIGGER_GROUPS = [
    {
        "group": "Price",
        "type_group": "price",
        "options": [
            {"id": "price-decrease", "label": "Price decreases"},
            {"id": "price-increase", "label": "Price increases"},
            {"id": "price-change", "label": "Price changes"},
        ],
    },
    {
        "group": "Stock",
        "type_group": "stock",
        "options": [
            {"id": "stock-out", "label": "Goes out of stock"},
            {"id": "stock-back", "label": "Comes back in stock"},
        ],
    },
    {
        "group": "Products",
        "type_group": "products",
        "options": [
            {"id": "product-new", "label": "New product"},
            {"id": "product-removed", "label": "Product removed"},
        ],
    },
    {
        "group": "Promotions",
        "type_group": "promotions",
        "options": [
            {"id": "promo-start", "label": "Promotion starts"},
            {"id": "promo-change", "label": "Promotion changes"},
            {"id": "promo-end", "label": "Promotion ends"},
        ],
    },
    {
        "group": "Competitor activity",
        "type_group": "patterns",
        "options": [
            {"id": "unusual-activity", "label": "Unusual activity"},
            {"id": "related-changes", "label": "Large group of related changes"},
        ],
    },
]

ALERT_FORM_OPTIONS = {
    "competitors": [
        "All competitors",
        "ToyWorld.co.uk",
        "PlayNest.co.uk",
        "HappyToyHouse.com",
        "LittleMindsToys.co.uk",
    ],
    "categories": [
        "All categories",
        "Outdoor Toys",
        "Educational Toys",
        "Construction Toys",
        "Baby Toys",
        "Plush Toys",
        "Personalised Toys",
    ],
    "operators": ["more than", "less than"],
    "priorities": [
        {"value": "high", "label": "High", "hint": "Important business activity."},
        {"value": "medium", "label": "Medium", "hint": "Worth monitoring."},
        {"value": "low", "label": "Low", "hint": "Informational."},
    ],
    "frequencies": [
        {"value": "Immediate", "hint": "Send whenever a matching new event occurs."},
        {"value": "Hourly summary", "hint": "Group matching alerts within an hour."},
        {"value": "Daily summary", "hint": "Send one digest per day."},
        {"value": "Weekly summary", "hint": "For low-priority monitoring."},
    ],
}

ALERT_FILTER_OPTIONS = {
    "statuses": [
        {"value": "all", "label": "All statuses"},
        {"value": "active", "label": "Active"},
        {"value": "paused", "label": "Paused"},
    ],
    "types": [
        {"value": "all", "label": "All types"},
        {"value": "price", "label": "Price"},
        {"value": "stock", "label": "Stock"},
        {"value": "products", "label": "Products"},
        {"value": "promotions", "label": "Promotions"},
        {"value": "patterns", "label": "Patterns"},
    ],
    "sorts": [
        {"value": "triggered", "label": "Recently triggered"},
        {"value": "created", "label": "Recently created"},
        {"value": "priority", "label": "Priority"},
        {"value": "name", "label": "Name"},
    ],
}

# Map a Changes-page change-type filter onto a create-alert trigger
# (ported from prototype-react/src/pages/alerts.tsx).
KIND_TO_TRIGGER = {
    "drop": "price-decrease",
    "increase": "price-increase",
    "oos": "stock-out",
    "back": "stock-back",
    "new": "product-new",
    "removed": "product-removed",
    "promo": "promo-start",
    "promo-end": "promo-end",
}
