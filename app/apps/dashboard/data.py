"""Mock data ported from prototype-react/src/lib/data.ts — deterministic seed for Phase 1."""

RANGES = [
    {"key": "today", "label": "Today"},
    {"key": "7d", "label": "7D"},
    {"key": "30d", "label": "30D"},
]

COMPETITORS = [
    {"name": "ToyWorld.co.uk", "market": "UK Toys Market"},
    {"name": "PlayNest.co.uk", "market": "UK Toys Market"},
    {"name": "HappyToyHouse.com", "market": "UK Toys Market"},
    {"name": "LittleMindsToys.co.uk", "market": "UK Toys Market"},
]

# 30d KPI rows: [id, label, value, tone] — shared verbatim by OVERVIEW_BY_RANGE["30d"].
KPIS = [
    ["monitored", "Products monitored", "2,438", "info"],
    ["new", "New products", "37", "success"],
    ["reductions", "Price reductions", "64", "success"],
    ["increases", "Price increases", "18", "danger"],
    ["oos", "Out of stock", "31", "warning"],
    ["promos", "New promotions", "7", "purple"],
]

PRICE_TREND = [
    {"date": "Apr 23", "median": 1.8, "average": 2.6},
    {"date": "Apr 26", "median": 0.9, "average": 1.7},
    {"date": "Apr 30", "median": -0.6, "average": 0.5},
    {"date": "May 3", "median": -2.1, "average": -1.1},
    {"date": "May 7", "median": -3.8, "average": -2.7},
    {"date": "May 10", "median": -5.2, "average": -4},
    {"date": "May 14", "median": -6.5, "average": -5.3},
    {"date": "May 17", "median": -7.3, "average": -6.1},
    {"date": "May 21", "median": -8.4, "average": -7},
]

CATEGORIES = [
    {"name": "Outdoor Toys", "value": 62},
    {"name": "Educational Toys", "value": 38},
    {"name": "Baby Toys", "value": 27},
    {"name": "Personalised Toys", "value": 22},
    {"name": "Plush Toys", "value": 18},
]

STOCK = [
    {"name": "In Stock", "value": 1872, "percent": "76.8%", "color": "#16a34a"},
    {"name": "Out of Stock", "value": 394, "percent": "16.2%", "color": "#ef4444"},
    {"name": "Back in Stock", "value": 172, "percent": "7.0%", "color": "#f59e0b"},
]

CHANGES = [
    {"id": "1", "product": "LEGO Castle Set", "sku": "TW-10432", "change": "Price drop", "old": "£59.99", "next": "£49.99", "stock": "In stock", "category": "Construction Toys", "time": "2h ago", "kind": "drop"},
    {"id": "2", "product": "STEM Robot Kit", "sku": "TW-20871", "change": "New promotion", "old": "—", "next": "20% off", "stock": "In stock", "category": "Educational Toys", "time": "3h ago", "kind": "promo"},
    {"id": "3", "product": "Wooden Balance Bike", "sku": "TW-30114", "change": "Out of stock", "old": "£89.00", "next": "£89.00", "stock": "Out of stock", "category": "Outdoor Toys", "time": "4h ago", "kind": "oos"},
    {"id": "4", "product": "Unicorn Plush XL", "sku": "TW-41208", "change": "New product", "old": "—", "next": "£24.99", "stock": "In stock", "category": "Plush Toys", "time": "6h ago", "kind": "new"},
    {"id": "5", "product": "Personalised Puzzle", "sku": "TW-50963", "change": "Name changed", "old": "£19.99", "next": "£19.99", "stock": "In stock", "category": "Personalised Toys", "time": "8h ago", "kind": "name"},
]

DISCOVERIES = [
    {"name": "PlayNest.co.uk", "match": 91, "tone": "blue"},
    {"name": "HappyToyHouse.com", "match": 88, "tone": "purple"},
    {"name": "LittleMindsToys.co.uk", "match": 85, "tone": "teal"},
    {"name": "BrightKidsPlay.com", "match": 82, "tone": "orange"},
]

# Per-range variants of the dashboard dataset so the global Today/7D/30D
# selector visibly changes the overview. 30d matches the original values;
# the backend will compute these per requested period.
OVERVIEW_BY_RANGE = {
    "30d": {
        "kpis": KPIS,
        "price_trend": PRICE_TREND,
        "categories": CATEGORIES,
        "stock": STOCK,
        "total_products": "2,438",
    },
    "7d": {
        "kpis": [
            ["monitored", "Products monitored", "2,438", "info"],
            ["new", "New products", "11", "success"],
            ["reductions", "Price reductions", "42", "success"],
            ["increases", "Price increases", "9", "danger"],
            ["oos", "Out of stock", "14", "warning"],
            ["promos", "New promotions", "3", "purple"],
        ],
        "price_trend": [
            {"date": "May 15", "median": -6.8, "average": -5.6},
            {"date": "May 16", "median": -7.0, "average": -5.8},
            {"date": "May 17", "median": -7.3, "average": -6.1},
            {"date": "May 18", "median": -7.6, "average": -6.3},
            {"date": "May 19", "median": -7.9, "average": -6.6},
            {"date": "May 20", "median": -8.2, "average": -6.8},
            {"date": "May 21", "median": -8.4, "average": -7},
        ],
        "categories": [
            {"name": "Outdoor Toys", "value": 58},
            {"name": "Educational Toys", "value": 41},
            {"name": "Baby Toys", "value": 22},
            {"name": "Personalised Toys", "value": 17},
            {"name": "Plush Toys", "value": 12},
        ],
        "stock": [
            {"name": "In Stock", "value": 1898, "percent": "77.9%", "color": "#16a34a"},
            {"name": "Out of Stock", "value": 381, "percent": "15.6%", "color": "#ef4444"},
            {"name": "Back in Stock", "value": 159, "percent": "6.5%", "color": "#f59e0b"},
        ],
        "total_products": "2,438",
    },
    "today": {
        "kpis": [
            ["monitored", "Products monitored", "2,438", "info"],
            ["new", "New products", "4", "success"],
            ["reductions", "Price reductions", "12", "success"],
            ["increases", "Price increases", "3", "danger"],
            ["oos", "Out of stock", "6", "warning"],
            ["promos", "New promotions", "2", "purple"],
        ],
        "price_trend": [
            {"date": "08:00", "median": -8.1, "average": -6.8},
            {"date": "09:00", "median": -8.1, "average": -6.9},
            {"date": "10:00", "median": -8.2, "average": -6.9},
            {"date": "11:00", "median": -8.3, "average": -7},
            {"date": "12:00", "median": -8.4, "average": -7},
            {"date": "13:00", "median": -8.4, "average": -7},
            {"date": "14:00", "median": -8.4, "average": -7},
        ],
        "categories": [
            {"name": "Outdoor Toys", "value": 64},
            {"name": "Educational Toys", "value": 31},
            {"name": "Baby Toys", "value": 12},
            {"name": "Personalised Toys", "value": 8},
            {"name": "Plush Toys", "value": 6},
        ],
        "stock": [
            {"name": "In Stock", "value": 1904, "percent": "78.1%", "color": "#16a34a"},
            {"name": "Out of Stock", "value": 388, "percent": "15.9%", "color": "#ef4444"},
            {"name": "Back in Stock", "value": 146, "percent": "6.0%", "color": "#f59e0b"},
        ],
        "total_products": "2,438",
    },
}
