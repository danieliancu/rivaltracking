"""Mock data ported from prototype-react/src/lib/reports-data.ts — deterministic seed for Phase 1."""

REPORT_TYPES = [
    {
        "id": "daily",
        "title": "Daily Intelligence",
        "description": "A concise summary of the most important competitor activity detected today.",
        "icon": "zap",
        "tone": "bg-info/10 text-info",
        "includes": ["Changes detected", "Biggest price movements", "New products", "AI executive summary"],
    },
    {
        "id": "weekly",
        "title": "Weekly Intelligence",
        "description": "Understand how competitors changed their catalogue and pricing over the last seven days.",
        "icon": "calendar-range",
        "tone": "bg-info/10 text-info",
        "includes": ["Weekly change totals", "Competitor comparison", "Price & stock trends", "AI strategic summary"],
    },
    {
        "id": "pricing",
        "title": "Pricing Analysis",
        "description": "Analyse pricing behaviour across competitors, categories and products.",
        "icon": "tags",
        "tone": "bg-success/10 text-success",
        "includes": ["Median price movement", "Biggest reductions & increases", "Price volatility", "Matched-product pricing"],
    },
    {
        "id": "launch",
        "title": "Product Launch Analysis",
        "description": "See what competitors have recently added to their catalogues.",
        "icon": "rocket",
        "tone": "bg-purple/10 text-purple",
        "includes": ["New products & variants", "Categories receiving launches", "Launch velocity", "Catalogue expansion patterns"],
    },
    {
        "id": "stock",
        "title": "Stock Analysis",
        "description": "Track stock availability and identify recurring supply patterns.",
        "icon": "package-x",
        "tone": "bg-warning/10 text-warning",
        "includes": ["Stock-outs & restocks", "Repeated stock-outs", "Affected categories", "Competitor stock stability"],
    },
    {
        "id": "promotion",
        "title": "Promotion Analysis",
        "description": "Understand current and historical competitor promotional activity.",
        "icon": "badge-percent",
        "tone": "bg-purple/10 text-purple",
        "includes": ["Promotions started & ended", "Discount levels", "Promoted categories", "Coordinated patterns"],
    },
    {
        "id": "category",
        "title": "Category Analysis",
        "description": "Analyse how a specific market category is changing across competitors.",
        "icon": "folder-search",
        "tone": "bg-teal/10 text-teal",
        "includes": ["Competitor presence", "Price movement", "New products", "Growth or contraction"],
    },
    {
        "id": "comparison",
        "title": "Competitor Comparison",
        "description": "Compare two or more competitors side by side.",
        "icon": "git-compare-arrows",
        "tone": "bg-info/10 text-info",
        "includes": ["Catalogue size", "Additions & removals", "Pricing activity", "Overlapping products"],
    },
    {
        "id": "market-gap",
        "title": "Market Gap Analysis",
        "description": "Identify catalogue and pricing opportunities across your monitored competitors.",
        "icon": "target",
        "tone": "bg-teal/10 text-teal",
        "includes": ["Low-coverage categories", "Unusual price gaps", "Frequently unavailable products", "Potential opportunities"],
    },
]

REPORT_KPIS = [
    {"id": "generated", "label": "Reports generated", "value": "28", "tone": "info"},
    {"id": "scheduled", "label": "Scheduled reports", "value": "3", "tone": "purple"},
    {"id": "covered", "label": "Competitors covered", "value": "4", "tone": "teal"},
    {"id": "latest", "label": "Latest report", "value": "Today, 08:00", "tone": "success"},
]

GENERATED_REPORTS = [
    {
        "id": "promotion-august",
        "name": "Promotion Analysis — August",
        "type_id": "promotion",
        "type": "Promotion Analysis",
        "competitors": "All",
        "period": "1–25 Aug",
        "created": "Just now",
        "status": "generating",
        "data_through": "25 Aug, 13:42",
    },
    {
        "id": "daily-25-aug",
        "name": "Daily Intelligence — 25 Aug",
        "type_id": "daily",
        "type": "Daily Intelligence",
        "competitors": "4",
        "period": "25 Aug",
        "created": "Today, 08:00",
        "status": "ready",
        "data_through": "25 Aug, 08:00",
    },
    {
        "id": "pricing-toys-market",
        "name": "Pricing Analysis — Toys Market",
        "type_id": "pricing",
        "type": "Pricing Analysis",
        "competitors": "ToyWorld + PlayNest",
        "period": "Last 30 days",
        "created": "Yesterday",
        "status": "ready",
        "data_through": "24 Aug, 18:10",
    },
    {
        "id": "weekly-week-34",
        "name": "Weekly Intelligence — Week 34",
        "type_id": "weekly",
        "type": "Weekly Intelligence",
        "competitors": "All",
        "period": "18–24 Aug",
        "created": "Yesterday",
        "status": "ready",
        "data_through": "24 Aug, 23:55",
    },
    {
        "id": "outdoor-toys-analysis",
        "name": "Outdoor Toys Analysis",
        "type_id": "category",
        "type": "Category Analysis",
        "competitors": "4",
        "period": "Last 30 days",
        "created": "2 days ago",
        "status": "ready",
        "data_through": "23 Aug, 21:30",
    },
    {
        "id": "stock-mid-august",
        "name": "Stock Analysis — Mid August",
        "type_id": "stock",
        "type": "Stock Analysis",
        "competitors": "All",
        "period": "8–15 Aug",
        "created": "1 week ago",
        "status": "attention",
        "note": "Some monitored pages could not be checked during this period.",
        "data_through": "15 Aug, 22:05",
    },
]

REPORT_SCHEDULES = [
    {"id": "s1", "name": "Daily Intelligence", "type_id": "daily", "frequency": "Every day", "time": "08:00", "competitors": "All competitors", "active": True},
    {"id": "s2", "name": "Weekly Intelligence", "type_id": "weekly", "frequency": "Every Monday", "time": "08:00", "competitors": "All competitors", "active": True},
    {"id": "s3", "name": "Pricing Report", "type_id": "pricing", "frequency": "Every Friday", "time": "16:00", "competitors": "ToyWorld + PlayNest", "active": True},
]

GENERATION_STAGES = [
    "Collecting historical data",
    "Calculating changes",
    "Analysing pricing and stock",
    "Detecting patterns",
    "Generating AI summary",
]

REPORT_FORM_OPTIONS = {
    "competitors": [
        "All monitored competitors",
        "ToyWorld.co.uk",
        "PlayNest.co.uk",
        "HappyToyHouse.com",
        "LittleMindsToys.co.uk",
    ],
    "date_ranges": ["Today", "Last 7 days", "Last 30 days", "Custom"],
    "categories": [
        "All categories",
        "Outdoor Toys",
        "Educational Toys",
        "Construction Toys",
        "Baby Toys",
        "Plush Toys",
        "Personalised Toys",
    ],
    "change_types": ["All changes", "Pricing", "Stock", "Products", "Promotions"],
    "frequencies": ["Daily", "Weekly", "Monthly"],
    "times": ["06:00", "08:00", "12:00", "16:00", "20:00"],
    "historical_since": "12 March 2026",
}

# Full structured dataset of the detailed weekly report — Python facts
# plus AI interpretation fields.
WEEKLY_REPORT = {
    "id": "weekly-week-34",
    "title": "Weekly Competitive Intelligence",
    "period": "18–24 August 2026",
    "competitors": "4 monitored companies",
    "generated": "25 August 2026, 08:00",
    "data_through": "25 Aug, 13:42",
    "executive_summary": "ToyWorld was the most active competitor this week, accounting for 48% of all detected catalogue changes. Pricing activity was concentrated in Outdoor Toys and Construction Toys, while PlayNest expanded its Educational Toys catalogue.",
    "key_takeaway": "The market currently shows stronger price competition in Outdoor Toys and catalogue expansion in Educational Toys.",
    "metrics": [
        {"id": "changes", "label": "Changes", "value": "428", "tone": "info"},
        {"id": "new", "label": "New Products", "value": "117", "tone": "info"},
        {"id": "drops", "label": "Price Drops", "value": "186", "tone": "success"},
        {"id": "increases", "label": "Price Increases", "value": "73", "tone": "danger"},
        {"id": "stockouts", "label": "Stock-outs", "value": "91", "tone": "warning"},
        {"id": "promos", "label": "Promotions", "value": "28", "tone": "purple"},
    ],
    "developments": [
        {
            "rank": 1,
            "title": "ToyWorld reduced Outdoor Toys pricing",
            "facts": ["42 products affected", "Average reduction -12.4%", "Started 22 Aug"],
            "evidence": {
                "label": "View 42 supporting changes",
                "to": "/changes?competitor=toyworld-co-uk&type=price-decrease&range=7d",
            },
            "tone": "bg-success/10 text-success",
        },
        {
            "rank": 2,
            "title": "PlayNest expanded Educational Toys",
            "facts": ["24 new products", "Main brands: STEM / Coding / Science"],
            "evidence": {
                "label": "View new products",
                "to": "/products?competitor=playnest-co-uk&change=new",
            },
            "tone": "bg-info/10 text-info",
        },
        {
            "rank": 3,
            "title": "HappyToyHouse stock availability declined",
            "facts": ["18 products unavailable", "Most affected: Construction Toys"],
            "evidence": {
                "label": "View stock changes",
                "to": "/changes?competitor=happytoyhouse-com&type=out-of-stock&range=7d",
            },
            "tone": "bg-warning/10 text-warning",
        },
    ],
    "pricing": {
        "facts": [
            {"label": "Price decreases", "value": "186", "tone": "text-success"},
            {"label": "Price increases", "value": "73", "tone": "text-destructive"},
            {"label": "Median decrease", "value": "-9.6%", "tone": "text-foreground"},
            {"label": "Largest detected reduction", "value": "-28%", "tone": "text-foreground"},
        ],
        "series": [
            {"day": "18 Aug", "decreases": 14, "increases": 9},
            {"day": "19 Aug", "decreases": 18, "increases": 11},
            {"day": "20 Aug", "decreases": 21, "increases": 12},
            {"day": "21 Aug", "decreases": 26, "increases": 8},
            {"day": "22 Aug", "decreases": 41, "increases": 12},
            {"day": "23 Aug", "decreases": 37, "increases": 10},
            {"day": "24 Aug", "decreases": 29, "increases": 11},
        ],
        "ai_note": "Pricing activity appears concentrated rather than market-wide. ToyWorld is responsible for most reductions.",
    },
    "catalogue": {
        "title": "Catalogue Intelligence",
        "facts": [
            {"label": "New products", "value": "117"},
            {"label": "Removed products", "value": "23"},
            {"label": "New variants", "value": "31"},
            {"label": "Category moves", "value": "9"},
        ],
        "ai_note": "Catalogue growth is driven mainly by PlayNest's Educational Toys additions.",
    },
    "stock": {
        "title": "Stock Intelligence",
        "facts": [
            {"label": "Stock-outs", "value": "91"},
            {"label": "Back in stock", "value": "44"},
            {"label": "Repeated availability problems", "value": "12"},
            {"label": "Most affected category", "value": "Construction Toys"},
        ],
        "ai_note": "Repeated stock-outs cluster around HappyToyHouse's Construction Toys range.",
    },
    "promotions": {
        "title": "Promotion Intelligence",
        "facts": [
            {"label": "Active promotions", "value": "19"},
            {"label": "Newly detected", "value": "28"},
            {"label": "Ended", "value": "11"},
            {"label": "Average discount", "value": "14%"},
        ],
        "ai_note": "Promotional activity remains moderate, led by ToyWorld's Educational Toys offers.",
    },
    "competitor_comparison": [
        {"name": "ToyWorld.co.uk", "products": 2438, "new_products": 21, "drops": 118, "increases": 24, "stockouts": 42, "promos": 14, "total": 206},
        {"name": "PlayNest.co.uk", "products": 1984, "new_products": 58, "drops": 31, "increases": 22, "stockouts": 15, "promos": 8, "total": 121},
        {"name": "HappyToyHouse.com", "products": 2103, "new_products": 22, "drops": 24, "increases": 17, "stockouts": 27, "promos": 4, "total": 74},
        {"name": "LittleMindsToys.co.uk", "products": 2221, "new_products": 16, "drops": 13, "increases": 10, "stockouts": 7, "promos": 2, "total": 27},
    ],
    "category_comparison": [
        {"name": "Outdoor Toys", "changes": 142},
        {"name": "Educational Toys", "changes": 96},
        {"name": "Construction Toys", "changes": 81},
        {"name": "Plush Toys", "changes": 44},
        {"name": "Baby Toys", "changes": 31},
    ],
    "opportunities": [
        "Educational Toys is expanding rapidly at PlayNest while pricing remains relatively stable across other competitors. This category may be worth investigating for catalogue gaps.",
        "Several Outdoor Toys products are frequently unavailable at two competitors — a potential opportunity if your availability is stable.",
    ],
    "risks": [
        "ToyWorld is applying sustained pricing pressure in Outdoor Toys, with 42 reductions averaging 12.4%.",
        "Repeated Construction Toys stock-outs at HappyToyHouse may shift demand unpredictably between competitors.",
    ],
    "recommended_actions": [
        "Review Outdoor Toys pricing.",
        "Compare your Educational Toys catalogue with new PlayNest additions.",
        "Monitor repeated stock-outs in Construction Toys.",
        "Watch ToyWorld promotion activity over the next seven days.",
    ],
}
