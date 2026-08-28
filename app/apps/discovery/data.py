"""Mock data ported from prototype-react/src/lib/discovery-data.ts — deterministic seed for Phase 1."""

DISCOVERY_CANDIDATES_SEED = [
    {
        "slug": "brightkidsplay-com",
        "name": "BrightKidsPlay.com",
        "url": "brightkidsplay.com",
        "match": 82,
        "tone": "orange",
        "cluster": "Educational Toys",
        "status": "suggested",
        "why_match": [
            "68% catalogue overlap with your monitored competitors",
            "Strong presence in Educational Toys and STEM kits",
            "Similar price band to ToyWorld.co.uk (£10–£90)",
            "Ships to the same UK market",
        ],
        "catalogue_profile": {
            "products": 1620,
            "categories": [
                {"name": "Educational Toys", "count": 540},
                {"name": "Construction Toys", "count": 380},
                {"name": "Outdoor Toys", "count": 290},
            ],
            "price_band": "£8 – £95",
            "overlap": "68% catalogue overlap",
        },
    },
    {
        "slug": "toycorner-co-uk",
        "name": "ToyCorner.co.uk",
        "url": "toycorner.co.uk",
        "match": 79,
        "tone": "blue",
        "cluster": "General Toys",
        "status": "suggested",
        "why_match": [
            "61% catalogue overlap across five shared categories",
            "Competes directly on Outdoor Toys pricing",
            "UK-based retailer with comparable catalogue size",
        ],
        "catalogue_profile": {
            "products": 2210,
            "categories": [
                {"name": "Outdoor Toys", "count": 610},
                {"name": "Plush Toys", "count": 420},
                {"name": "Baby Toys", "count": 300},
            ],
            "price_band": "£5 – £120",
            "overlap": "61% catalogue overlap",
        },
    },
    {
        "slug": "kidsplaystore-co-uk",
        "name": "KidsPlayStore.co.uk",
        "url": "kidsplaystore.co.uk",
        "match": 76,
        "tone": "teal",
        "cluster": "Outdoor Toys",
        "status": "suggested",
        "why_match": [
            "57% catalogue overlap, concentrated in Outdoor Toys",
            "Frequently discounts the same product lines as ToyWorld",
            "Similar seasonal promotion cadence",
        ],
        "catalogue_profile": {
            "products": 1480,
            "categories": [
                {"name": "Outdoor Toys", "count": 520},
                {"name": "Garden Play", "count": 260},
                {"name": "Sports Toys", "count": 190},
            ],
            "price_band": "£12 – £150",
            "overlap": "57% catalogue overlap",
        },
    },
    {
        "slug": "smartplaytoys-co-uk",
        "name": "SmartPlayToys.co.uk",
        "url": "smartplaytoys.co.uk",
        "match": 73,
        "tone": "purple",
        "cluster": "Educational Toys",
        "status": "suggested",
        "why_match": [
            "54% catalogue overlap in Educational and STEM ranges",
            "Overlapping brand portfolio with PlayNest.co.uk",
            "Comparable price positioning",
        ],
        "catalogue_profile": {
            "products": 980,
            "categories": [
                {"name": "Educational Toys", "count": 460},
                {"name": "Science Kits", "count": 210},
                {"name": "Puzzles", "count": 140},
            ],
            "price_band": "£10 – £80",
            "overlap": "54% catalogue overlap",
        },
    },
    {
        "slug": "gardenplaydirect-com",
        "name": "GardenPlayDirect.com",
        "url": "gardenplaydirect.com",
        "match": 69,
        "tone": "orange",
        "cluster": "Outdoor Toys",
        "status": "suggested",
        "why_match": [
            "Specialist Outdoor Toys retailer with 48% overlap",
            "Competes on large garden items where your competitors discount",
        ],
        "catalogue_profile": {
            "products": 720,
            "categories": [
                {"name": "Outdoor Toys", "count": 480},
                {"name": "Garden Play", "count": 160},
            ],
            "price_band": "£25 – £400",
            "overlap": "48% catalogue overlap",
        },
    },
    {
        "slug": "littleexplorers-co-uk",
        "name": "LittleExplorers.co.uk",
        "url": "littleexplorers.co.uk",
        "match": 66,
        "tone": "teal",
        "cluster": "General Toys",
        "status": "suggested",
        "why_match": [
            "45% catalogue overlap across Baby and Plush Toys",
            "Growing catalogue in categories your competitors expand into",
        ],
        "catalogue_profile": {
            "products": 1150,
            "categories": [
                {"name": "Baby Toys", "count": 380},
                {"name": "Plush Toys", "count": 310},
                {"name": "Educational Toys", "count": 240},
            ],
            "price_band": "£6 – £70",
            "overlap": "45% catalogue overlap",
        },
    },
]

DISCOVERY_CLUSTERS = [
    {"id": "Educational Toys", "label": "Educational Toys"},
    {"id": "Outdoor Toys", "label": "Outdoor Toys"},
    {"id": "General Toys", "label": "General Toys"},
]

DISCOVERY_MODES = [
    {"value": "existing", "label": "Based on existing competitors"},
    {"value": "website", "label": "From a website"},
    {"value": "category", "label": "By category"},
    {"value": "brand", "label": "By brand"},
    {"value": "market", "label": "By market"},
]

DISCOVERY_STAGES = [
    "Analysing your market",
    "Finding candidate companies",
    "Comparing catalogues",
    "Ranking matches",
]
