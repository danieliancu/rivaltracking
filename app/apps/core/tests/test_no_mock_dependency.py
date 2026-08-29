"""Production code must not depend on the Phase 1 fabricated business datasets."""
import pathlib
import re

import pytest

APP_ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../app/apps

# Files that are allowed to reference demo data: seed sources, the seed command,
# tests, migrations, and the data.py modules themselves.
ALLOWED_NAMES = {"data.py", "seed.py", "seed_demo.py", "constants.py"}

DEMO_NAMES = ["ToyWorld", "PlayNest", "HappyToyHouse", "LittleMinds", "BrightKidsPlay"]
BUSINESS_SEEDS = [
    "COMPETITOR_ROWS", "PRODUCTS", "CHANGE_EVENTS", "ALERT_RULES", "RECENT_ALERTS",
    "GENERATED_REPORTS", "REPORT_SCHEDULES", "DISCOVERY_CANDIDATES_SEED",
    "CONVERSATION_HISTORY", "WEEKLY_REPORT", "RESPONSES", "FALLBACK_RESPONSE",
    "CANDIDATE_RESPONSE_TEMPLATE", "ACTIVITY_EVENTS", "CHANGE_ACTIVITY",
    "COMPETITOR_ACTIVITY", "CHANGE_PATTERNS", "PRICE_MOVEMENT", "ACTIVE_CATEGORIES",
    "ALERT_ACTIVITY", "MOST_TRIGGERED_RULES", "ALERT_COVERAGE", "REPORT_KPIS",
    "TOYWORLD_PROFILE", "TEAM_MEMBERS",
]


def _production_files():
    for path in APP_ROOT.rglob("*.py"):
        posix = path.as_posix()
        if any(part in posix for part in ("/tests/", "/migrations/")):
            continue
        if path.name in ALLOWED_NAMES:
            continue
        if "__pycache__" in posix:
            continue
        yield path


def test_production_has_no_demo_company_names():
    offenders = []
    for path in _production_files():
        text = path.read_text(encoding="utf-8")
        for name in DEMO_NAMES:
            if name in text:
                offenders.append(f"{path.name}: {name}")
    assert not offenders, f"Demo company names in production code: {offenders}"


def test_production_does_not_import_business_seeds():
    offenders = []
    for path in _production_files():
        text = path.read_text(encoding="utf-8")
        for seed in BUSINESS_SEEDS:
            if re.search(r"" + seed + r"", text):
                offenders.append(f"{path.name}: {seed}")
    assert not offenders, f"Production code references fabricated business seeds: {offenders}"
