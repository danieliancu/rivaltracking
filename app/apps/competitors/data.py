"""Mock data ported from prototype-react/src/lib/competitors-data.ts — deterministic seed for Phase 1."""

COMPETITOR_ROWS = [
    {
        "slug": "toyworld-co-uk",
        "name": "ToyWorld.co.uk",
        "url": "toyworld.co.uk",
        "market": "UK Toys",
        "products": 2438,
        "changes_today": 67,
        "price_drops": 64,
        "price_increases": 18,
        "stock_changes": 31,
        "last_scan": "12 min ago",
        "last_scan_minutes": 12,
        "status": "healthy",
        "added_at": "2026-03-02",
    },
    {
        "slug": "playnest-co-uk",
        "name": "PlayNest.co.uk",
        "url": "playnest.co.uk",
        "market": "UK Toys",
        "products": 1984,
        "changes_today": 31,
        "price_drops": 21,
        "price_increases": 7,
        "stock_changes": 14,
        "last_scan": "26 min ago",
        "last_scan_minutes": 26,
        "status": "healthy",
        "added_at": "2026-04-18",
    },
    {
        "slug": "happytoyhouse-com",
        "name": "HappyToyHouse.com",
        "url": "happytoyhouse.com",
        "market": "UK Toys",
        "products": 2103,
        "changes_today": 19,
        "price_drops": 8,
        "price_increases": 4,
        "stock_changes": 7,
        "last_scan": "1h ago",
        "last_scan_minutes": 60,
        "status": "attention",
        "note": "Some product pages could not be scanned.",
        "added_at": "2026-05-30",
    },
    {
        "slug": "littlemindstoys-co-uk",
        "name": "LittleMindsToys.co.uk",
        "url": "littlemindstoys.co.uk",
        "market": "UK Toys",
        "products": 2221,
        "changes_today": 4,
        "price_drops": 2,
        "price_increases": 1,
        "stock_changes": 1,
        "last_scan": "Scanning now",
        "last_scan_minutes": 0,
        "status": "scanning",
        "added_at": "2026-07-11",
    },
]

COMPETITOR_KPIS = [
    {"id": "competitors", "label": "Monitored competitors", "value": "4", "tone": "info"},
    {"id": "products", "label": "Products monitored", "value": "8,746", "tone": "info"},
    {"id": "changes", "label": "Changes today", "value": "121", "tone": "success"},
    {"id": "attention", "label": "Attention required", "value": "2", "tone": "warning"},
]

ACTIVITY_EVENTS = [
    {"company": "ToyWorld.co.uk", "event": "64 prices reduced", "time": "12 min ago", "kind": "prices-down"},
    {"company": "PlayNest.co.uk", "event": "11 new products discovered", "time": "26 min ago", "kind": "new-products"},
    {"company": "HappyToyHouse.com", "event": "7 product pages unavailable", "time": "1h ago", "kind": "pages-unavailable"},
    {"company": "ToyWorld.co.uk", "event": "31 products went out of stock", "time": "2h ago", "kind": "out-of-stock"},
    {"company": "LittleMindsToys.co.uk", "event": "New promotion detected in Educational Toys", "time": "3h ago", "kind": "promotion"},
]

DISCOVERY_SUGGESTIONS = [
    {"name": "BrightKidsPlay.com", "match": 82, "tone": "orange"},
    {"name": "ToyCorner.co.uk", "match": 79, "tone": "blue"},
    {"name": "KidsPlayStore.co.uk", "match": 76, "tone": "teal"},
]

MONITORING_HEALTH = {
    "healthy": 3,
    "attention": 1,
    "last_successful_scan": "12 minutes ago",
    "next_scheduled_scan": "in 48 minutes",
}

# Stages simulated by the Add Competitor onboarding flow.
SCAN_STAGES = [
    "Detecting website",
    "Discovering catalogue",
    "Finding products",
    "Creating initial snapshot",
    "Monitoring enabled",
]

ADDED_COMPETITOR_RESULT = {
    "name": "ToyPlanet.co.uk",
    "slug": "toyplanet-co-uk",
    "url": "toyplanet.co.uk",
    "products": 1824,
    "categories": 31,
}
