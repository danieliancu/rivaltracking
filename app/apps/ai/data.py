"""Mock data ported from prototype-react/src/lib/ask-ai-data.ts — deterministic seed for Phase 1.

resolveResponse algorithm (implemented by services, not here):
- If the query context marks a discovery candidate (candidate=True) and names a
  competitor, short-circuit and return CANDIDATE_RESPONSE_TEMPLATE formatted with
  that competitor's name.
- Otherwise scan RESPONSES in order and return the first entry whose regex
  pattern matches the question (patterns are matched case-insensitively —
  compile with re.IGNORECASE); fall back to FALLBACK_RESPONSE when none match.
- If the context carries scope parts (competitor, product, category, period, or
  scope == "all-competitors" rendered as "All competitors"), prepend the prefix
  "Scoped to X · Y. " (parts joined with " · ") to the response summary.
"""

DATA_THROUGH = "25 Aug, 14:42"
TOYWORLD_SCAN = "Last ToyWorld scan: 12 min ago"

SUGGESTED_QUESTIONS = [
    {"category": "Today", "question": "What should I pay attention to today?"},
    {"category": "Pricing", "question": "Which competitors reduced prices this week?"},
    {"category": "Products", "question": "What new products have appeared recently?"},
    {"category": "Stock", "question": "Where are competitors having stock problems?"},
    {"category": "Strategy", "question": "Is ToyWorld showing signs of a pricing campaign?"},
    {"category": "Opportunities", "question": "Find potential gaps in competitor catalogues."},
]

ACTIVITY_SUGGESTIONS = [
    {
        "title": "ToyWorld pricing spike",
        "detail": "67 changes detected",
        "cta": "Ask what changed",
        "prompt": "What changed at ToyWorld this week?",
        "tone": "bg-success/10 text-success",
    },
    {
        "title": "Educational Toys expansion",
        "detail": "14 new products detected at PlayNest",
        "cta": "Analyse",
        "prompt": "What new products have appeared recently?",
        "tone": "bg-info/10 text-info",
    },
    {
        "title": "Stock activity",
        "detail": "18 products unavailable at HappyToyHouse",
        "cta": "Investigate",
        "prompt": "Where are competitors having stock problems?",
        "tone": "bg-warning/10 text-warning",
    },
]

CONVERSATION_HISTORY = [
    {"id": "c1", "title": "ToyWorld weekly activity", "when": "Today"},
    {"id": "c2", "title": "Outdoor Toys pricing", "when": "Today"},
    {"id": "c3", "title": "Compare ToyWorld vs PlayNest", "when": "Yesterday"},
    {"id": "c4", "title": "Catalogue opportunities", "when": "22 Aug"},
]

# Canned responses: first pattern match wins (case-insensitive; services
# compile these pattern strings with re.IGNORECASE).
RESPONSES = [
    {
        "id": "toyworld-week",
        "pattern": r"(changed|change|active).*toyworld|toyworld.*(week|changed|activity)",
        "response": {
            "id": "toyworld-week",
            "heading": "ToyWorld was highly active this week",
            "summary": "428 changes were detected across 2,438 monitored products.",
            "bullets": [
                "**186** price decreases",
                "**73** price increases",
                "**31** stock-outs",
                "**37** new products",
                "**7** new promotions",
            ],
            "metrics": [
                {"label": "Price decreases", "value": "186", "tone": "text-success"},
                {"label": "Price increases", "value": "73", "tone": "text-destructive"},
                {"label": "New products", "value": "37"},
                {"label": "Stock changes", "value": "31"},
            ],
            "interpretation": "The strongest activity was in Outdoor Toys, where median prices fell by 8.4%. ToyWorld was responsible for approximately 48% of all competitor activity monitored during this period — it appears to be applying concentrated pricing pressure rather than making random isolated adjustments.",
            "next_step": "Review your Outdoor Toys pricing and inspect ToyWorld's largest reductions.",
            "evidence": [
                {"label": "View 186 price changes", "to": "/changes"},
                {"label": "View 37 new products", "to": "/products"},
                {"label": "View Outdoor Toys category", "to": "/products"},
            ],
            "follow_ups": [
                "Which products had the biggest reductions?",
                "Compare this with PlayNest",
                "Show ToyWorld price activity over the last 30 days",
                "Create an alert for drops over 10%",
            ],
            "actions": [
                {
                    "label": "Create alert",
                    "kind": "alert",
                    "alert_prefill": {"competitor": "ToyWorld.co.uk", "kind": "drop"},
                },
                {
                    "label": "View in Changes",
                    "kind": "changes",
                    "to": "/changes?competitor=toyworld-co-uk",
                },
            ],
            "data_through": DATA_THROUGH,
            "last_scan": TOYWORLD_SCAN,
        },
    },
    {
        "id": "attention-today",
        "pattern": r"attention|investigate today|pay attention|should i (look|investigate)",
        "response": {
            "id": "attention-today",
            "heading": "ToyWorld has the highest activity today",
            "summary": "ToyWorld accounts for 55% of all detected competitor changes.",
            "bullets": [
                "**42** price decreases in Outdoor Toys",
                "Median reduction of **12.4%**",
                "**8** new promotions",
                "**11** products currently out of stock",
            ],
            "interpretation": "PlayNest is also showing notable activity, primarily through 14 new Educational Toys. The concentration and timing of ToyWorld's reductions suggest a coordinated campaign rather than isolated adjustments.",
            "recommendations": [
                "ToyWorld's Outdoor Toys pricing",
                "PlayNest's new Educational Toys",
                "Stock availability at HappyToyHouse",
            ],
            "evidence": [
                {"label": "View 67 ToyWorld changes", "to": "/changes"},
                {"label": "View 14 PlayNest products", "to": "/products"},
                {"label": "View stock activity", "to": "/changes"},
            ],
            "follow_ups": [
                "Why do you think ToyWorld is doing this?",
                "Compare ToyWorld with my other competitors",
                "Create a price alert",
            ],
            "actions": [{"label": "Create alert", "kind": "alert"}],
            "data_through": DATA_THROUGH,
            "last_scan": TOYWORLD_SCAN,
        },
    },
    {
        "id": "biggest-drops",
        "pattern": r"biggest|largest|drops over|reduced prices|price drops|reductions",
        "response": {
            "id": "biggest-drops",
            "heading": "Largest price reductions this week",
            "summary": "186 price decreases were detected. These are the largest verified reductions:",
            "product_list": {
                "title": "Largest price reductions",
                "items": [
                    {"name": "LEGO Castle Set", "slug": "lego-castle-set", "from": "£59.99", "to": "£49.99", "pct": "-16.7%"},
                    {"name": "STEM Robot Kit", "slug": "stem-robot-kit", "from": "£47.99", "to": "£39.99", "pct": "-16.7%"},
                    {"name": "Wooden Train Set", "slug": "wooden-train-set", "from": "£37.99", "to": "£32.99", "pct": "-13.2%"},
                ],
            },
            "interpretation": "Most of these reductions belong to ToyWorld's Outdoor and Construction Toys ranges, consistent with a concentrated campaign.",
            "evidence": [
                {"label": "View 42 supporting changes", "to": "/changes"},
                {"label": "View products", "to": "/products"},
            ],
            "follow_ups": [
                "Compare this with PlayNest",
                "Show the last 30 days",
                "Create an alert for drops over 10%",
            ],
            "actions": [
                {"label": "View in Changes", "kind": "changes"},
                {"label": "Create alert", "kind": "alert"},
            ],
            "data_through": DATA_THROUGH,
            "last_scan": TOYWORLD_SCAN,
        },
    },
    {
        "id": "compare",
        "pattern": r"compare",
        "response": {
            "id": "compare",
            "heading": "Competitor comparison — this week",
            "summary": "Verified activity across your four monitored competitors:",
            "comparison_table": [
                {"competitor": "ToyWorld.co.uk", "changes": 67, "drops": 42, "new_products": 11},
                {"competitor": "PlayNest.co.uk", "changes": 31, "drops": 12, "new_products": 14},
                {"competitor": "HappyToyHouse.com", "changes": 19, "drops": 8, "new_products": 4},
                {"competitor": "LittleMindsToys.co.uk", "changes": 4, "drops": 2, "new_products": 1},
            ],
            "interpretation": "ToyWorld competes mainly on price while PlayNest competes on catalogue breadth — two different strategies emerging in the same market.",
            "caveat": "HappyToyHouse has partial monitoring data for today because some product pages could not be checked. Results involving this competitor may be incomplete.",
            "evidence": [
                {"label": "View competitor activity", "to": "/competitors"},
                {"label": "View all changes", "to": "/changes"},
            ],
            "follow_ups": [
                "Which categories are they discounting?",
                "What is unusual about ToyWorld's behaviour?",
                "Create a Pricing Report",
            ],
            "actions": [
                {"label": "Create Pricing Report", "kind": "report", "report_type_id": "pricing"},
            ],
            "data_through": DATA_THROUGH,
        },
    },
    {
        "id": "price-chart",
        "pattern": r"price activity|over the last 30|chart|trend",
        "response": {
            "id": "price-chart",
            "heading": "ToyWorld price activity — last 30 days",
            "summary": "Detected price changes per week. Activity accelerated sharply in the most recent week:",
            "chart": {
                "title": "Price changes per week",
                "series": [
                    {"label": "Week 31", "value": 22},
                    {"label": "Week 32", "value": 31},
                    {"label": "Week 33", "value": 26},
                    {"label": "Week 34", "value": 118},
                ],
            },
            "interpretation": "The Week 34 spike coincides with the Outdoor Toys reductions — sustained, not a one-day adjustment.",
            "evidence": [{"label": "View underlying changes", "to": "/changes"}],
            "follow_ups": [
                "Which products had the biggest reductions?",
                "Is this concentrated in one category?",
            ],
            "data_through": DATA_THROUGH,
            "last_scan": TOYWORLD_SCAN,
        },
    },
    {
        "id": "new-products",
        "pattern": r"new products|appeared|added|launch",
        "response": {
            "id": "new-products",
            "heading": "117 new products appeared this month",
            "summary": "PlayNest leads catalogue expansion, adding 58 products — mostly Educational Toys.",
            "metrics": [
                {"label": "PlayNest", "value": "58"},
                {"label": "ToyWorld", "value": "21"},
                {"label": "HappyToyHouse", "value": "22"},
                {"label": "LittleMinds", "value": "16"},
            ],
            "interpretation": "Products discovered during initial baseline scans are excluded — these counts reflect only post-baseline additions.",
            "evidence": [{"label": "View new products", "to": "/products"}],
            "follow_ups": [
                "Which categories are receiving most launches?",
                "Compare launch velocity across competitors",
            ],
            "actions": [{"label": "View products", "kind": "products"}],
            "data_through": DATA_THROUGH,
        },
    },
    {
        "id": "stock",
        "pattern": r"stock|unavailable|out of stock",
        "response": {
            "id": "stock",
            "heading": "Stock problems concentrate at HappyToyHouse",
            "summary": "91 stock-outs were detected this week. 18 products are currently unavailable at HappyToyHouse, mostly Construction Toys.",
            "metrics": [
                {"label": "Stock-outs this week", "value": "91", "tone": "text-warning"},
                {"label": "Back in stock", "value": "44", "tone": "text-success"},
                {"label": "Repeated problems", "value": "12"},
            ],
            "interpretation": "Repeated Construction Toys stock-outs may shift demand between competitors — worth watching if your availability is stable.",
            "caveat": "HappyToyHouse has partial monitoring data for today because some product pages could not be checked. Results involving this competitor may be incomplete.",
            "evidence": [{"label": "View stock changes", "to": "/changes"}],
            "follow_ups": [
                "Which products are repeatedly out of stock?",
                "Create a stock alert",
            ],
            "actions": [{"label": "Create alert", "kind": "alert"}],
            "data_through": DATA_THROUGH,
        },
    },
    {
        "id": "gaps",
        "pattern": r"gap|opportunit",
        "response": {
            "id": "gaps",
            "heading": "Potential catalogue opportunities",
            "summary": "Based on verified coverage and availability data, two areas stand out as worth investigating:",
            "bullets": [
                "**Educational Toys** — expanding rapidly at PlayNest while pricing stays stable elsewhere",
                "**Outdoor Toys availability** — several products frequently unavailable at two competitors",
            ],
            "interpretation": "These are potential opportunities, not guaranteed gaps — coverage and demand should be verified before acting.",
            "evidence": [
                {"label": "View category activity", "to": "/products"},
                {"label": "View stock changes", "to": "/changes"},
            ],
            "follow_ups": [
                "Which products are unique to one competitor?",
                "Create a Market Gap report",
            ],
            "actions": [
                {"label": "Create Pricing Report", "kind": "report", "report_type_id": "pricing"},
            ],
            "data_through": DATA_THROUGH,
        },
    },
]

FALLBACK_RESPONSE = {
    "id": "fallback",
    "heading": "Today's competitor activity at a glance",
    "summary": "121 verified changes were detected today across your 4 monitored competitors.",
    "metrics": [
        {"label": "Changes today", "value": "121"},
        {"label": "Price decreases", "value": "64", "tone": "text-success"},
        {"label": "New products", "value": "37"},
        {"label": "Stock changes", "value": "31", "tone": "text-warning"},
    ],
    "interpretation": "Most activity concentrates at ToyWorld. Ask me about a competitor, category or product for a deeper analysis.",
    "caveat": "HappyToyHouse has partial monitoring data for today because some product pages could not be checked. Results involving this competitor may be incomplete.",
    "evidence": [{"label": "View today's changes", "to": "/changes"}],
    "follow_ups": [
        "What should I pay attention to today?",
        "What changed at ToyWorld this week?",
        "Compare my competitors",
    ],
    "data_through": DATA_THROUGH,
}

# Response for unmonitored discovery candidates. Services format the string
# fields containing "{name}" with str.format(name=<candidate name>).
CANDIDATE_RESPONSE_TEMPLATE = {
    "id": "candidate-{name}",
    "heading": "{name} is not monitored yet",
    "summary": "{name} was found by the Discovery Engine, so only its current catalogue profile is available — there is no price or stock history until monitoring starts.",
    "bullets": [
        "**Catalogue profile** — categories and price bands from the discovery comparison",
        "**No change history** — changes are only recorded for monitored competitors",
    ],
    "interpretation": "Start monitoring this company to build an initial snapshot. Historical comparisons become available after the second successful scan.",
    "next_step": "Monitor {name} from the Discovery page to start collecting data.",
    "evidence": [{"label": "View discovery results", "to": "/discovery"}],
    "follow_ups": [
        "Compare this candidate with my monitored competitors",
        "What should I pay attention to today?",
    ],
    "data_through": DATA_THROUGH,
}
