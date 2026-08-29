"""Deterministic demo seeding: turn the Phase 1 fixture dicts into ORM rows.

`seed_workspace(workspace)` is idempotent — it clears the workspace's business
data first, then rebuilds it from the same `apps/<app>/data.py` seeds the mock
store used, so every Phase 1 screen keeps its exact content. Timestamps are
anchored to "now" so relative-time labels ("2h ago") render as before.

Both the `seed_demo` management command and the test fixtures call this, so the
demo and the tests exercise identical data.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.catalogue.models import (
    OwnProduct,
    PriceSnapshot,
    Product,
    ProductListing,
    Promotion,
    StockSnapshot,
    StockStatus,
)
from apps.changes.models import ChangeEvent
from apps.competitors.models import Competitor
from apps.core.entities import competitor_tone
from apps.products.models import WatchlistItem

EVENT_TYPE_MAP = {
    "PRICE_DECREASE": ChangeEvent.Type.PRICE_DECREASE,
    "PRICE_INCREASE": ChangeEvent.Type.PRICE_INCREASE,
    "STOCK_OUT": ChangeEvent.Type.STOCK_OUT,
    "STOCK_BACK": ChangeEvent.Type.STOCK_IN,
    "PRODUCT_NEW": ChangeEvent.Type.PRODUCT_NEW,
    "PRODUCT_REMOVED": ChangeEvent.Type.PRODUCT_REMOVED,
    "PROMOTION_STARTED": ChangeEvent.Type.PROMOTION_STARTED,
    "PROMOTION_ENDED": ChangeEvent.Type.PROMOTION_ENDED,
    "NAME_CHANGED": ChangeEvent.Type.PRODUCT_METADATA_CHANGE,
    "CATEGORY_CHANGED": ChangeEvent.Type.PRODUCT_METADATA_CHANGE,
    "DESCRIPTION_CHANGED": ChangeEvent.Type.PRODUCT_METADATA_CHANGE,
    "VARIANT_ADDED": ChangeEvent.Type.PRODUCT_METADATA_CHANGE,
    "VARIANT_REMOVED": ChangeEvent.Type.PRODUCT_METADATA_CHANGE,
}


def _dec(value):
    return None if value is None else Decimal(str(value))


def _stock(in_stock):
    return StockStatus.IN_STOCK if in_stock else StockStatus.OUT_OF_STOCK


def clear_workspace_data(workspace):
    """Remove all business rows for a workspace (safe to call repeatedly)."""
    ChangeEvent.objects.filter(workspace=workspace).delete()
    Promotion.objects.filter(workspace=workspace).delete()
    PriceSnapshot.objects.filter(workspace=workspace).delete()
    StockSnapshot.objects.filter(workspace=workspace).delete()
    WatchlistItem.objects.filter(workspace=workspace).delete()
    ProductListing.objects.filter(workspace=workspace).delete()
    OwnProduct.objects.filter(workspace=workspace).delete()
    Product.objects.filter(workspace=workspace).delete()
    Competitor.objects.filter(workspace=workspace).delete()


def _seed_competitors(workspace, now):
    from apps.competitors.data import COMPETITOR_ROWS

    by_name = {}
    for row in COMPETITOR_ROWS:
        minutes = row.get("last_scan_minutes")
        if row["status"] == "scanning":
            last_scan_at = now
        elif minutes is None:
            last_scan_at = None
        else:
            last_scan_at = now - timedelta(minutes=minutes)
        competitor = Competitor.objects.create(
            workspace=workspace,
            name=row["name"],
            slug=row["slug"],
            domain=row["url"],
            website_url=f"https://{row['url']}",
            market=row.get("market", ""),
            status=row["status"],
            monitoring_enabled=row["status"] != "paused",
            note=row.get("note", ""),
            tone=competitor_tone(row["name"]),
            products_count=row.get("products"),
            changes_today=row.get("changes_today"),
            price_drops=row.get("price_drops"),
            price_increases=row.get("price_increases"),
            stock_changes=row.get("stock_changes"),
            added_at=row["added_at"],
            last_scan_at=last_scan_at,
            next_scan_at=now + timedelta(hours=24),
        )
        by_name[row["name"]] = competitor
    return by_name


def _icons_by_slug():
    from apps.changes.data import CHANGE_EVENTS

    return {e["product"]["slug"]: e["product"].get("icon", "package") for e in CHANGE_EVENTS}


def _seed_products(workspace, competitors, now):
    from apps.products.data import PRODUCTS

    icons = _icons_by_slug()
    products = {}
    primary_listing = {}

    for row in PRODUCTS:
        matched = row.get("matched") or {}
        product = Product.objects.create(
            workspace=workspace,
            name=row["name"],
            slug=row["slug"],
            sku=row["sku"],
            category=row["category"],
            tone=row.get("tone") or "",
            icon=icons.get(row["slug"], "package"),
            image_url=row.get("image") or "",
            match_confidence=matched.get("confidence"),
            match_insight=matched.get("insight", ""),
        )
        products[row["slug"]] = product

        first_seen = None
        if row.get("discovered_at"):
            first_seen = timezone.make_aware(
                timezone.datetime.fromisoformat(row["discovered_at"])
            )
        primary_competitor = competitors[row["competitor"]]
        listing = ProductListing.objects.create(
            workspace=workspace,
            product=product,
            competitor=primary_competitor,
            source_url=row.get("source_url", ""),
            competitor_sku=row["sku"],
            competitor_product_name=row["name"],
            current_price=_dec(row.get("current_price")),
            previous_price=_dec(row.get("previous_price")),
            current_stock_status=_stock(row.get("in_stock", True)),
            is_primary=True,
            change_kind=row["change"]["kind"],
            change_label=row["change"]["label"],
            last_change_at=now - timedelta(minutes=row.get("last_change_minutes", 0)),
            first_seen_at=first_seen,
            last_seen_at=now,
        )
        primary_listing[row["slug"]] = listing

        # Additional competitor listings from the "matched" block.
        for m in row.get("matched", {}).get("listings", []):
            competitor = competitors.get(m["competitor"])
            if competitor is None or competitor == primary_competitor:
                if competitor == primary_competitor and m.get("promotion"):
                    listing.current_promotion = m["promotion"]
                    listing.save(update_fields=["current_promotion"])
                continue
            ProductListing.objects.create(
                workspace=workspace,
                product=product,
                competitor=competitor,
                source_url="",
                competitor_sku=row["sku"],
                competitor_product_name=row["name"],
                current_price=_dec(m.get("price")),
                current_stock_status=_stock(m.get("in_stock", True)),
                current_promotion=m.get("promotion") or "",
                is_primary=False,
                last_seen_at=now,
            )

    return products, primary_listing


def _seed_history(workspace, primary_listing, now):
    price_rows, stock_rows, promo_rows = [], [], []
    for slug, listing in primary_listing.items():
        current = float(listing.current_price) if listing.current_price is not None else None
        previous = float(listing.previous_price) if listing.previous_price is not None else None
        rnd = random.Random(sum(ord(c) for c in slug))
        if current is not None:
            base = previous or current
            for i in range(29, -1, -1):
                captured = now - timedelta(days=i)
                if i == 0:
                    price = current
                elif i == 1 and previous is not None:
                    price = previous
                else:
                    price = round(base * (1 + rnd.uniform(-0.06, 0.06)), 2)
                price_rows.append(
                    PriceSnapshot(
                        workspace=workspace,
                        listing=listing,
                        price=Decimal(str(price)),
                        captured_at=captured,
                    )
                )
        for i in range(29, -1, -1):
            captured = now - timedelta(days=i)
            status = listing.current_stock_status if i == 0 else StockStatus.IN_STOCK
            stock_rows.append(
                StockSnapshot(
                    workspace=workspace,
                    listing=listing,
                    stock_status=status,
                    captured_at=captured,
                )
            )
        if listing.current_promotion or listing.change_kind == "promo":
            promo_rows.append(
                Promotion(
                    workspace=workspace,
                    listing=listing,
                    title=listing.current_promotion or listing.change_label,
                    promotion_type="percentage",
                    value=listing.current_promotion or listing.change_label,
                    started_at=now - timedelta(days=2),
                    active=True,
                    captured_at=now,
                )
            )
    PriceSnapshot.objects.bulk_create(price_rows)
    StockSnapshot.objects.bulk_create(stock_rows)
    Promotion.objects.bulk_create(promo_rows)


def _seed_change_events(workspace, competitors, products, primary_listing, now):
    from apps.changes.data import CHANGE_EVENTS

    for e in CHANGE_EVENTS:
        slug = e["product"]["slug"]
        ChangeEvent.objects.create(
            workspace=workspace,
            competitor=competitors[e["competitor"]],
            product=products.get(slug),
            listing=primary_listing.get(slug),
            event_type=EVENT_TYPE_MAP.get(
                e["type"], ChangeEvent.Type.PRODUCT_METADATA_CHANGE
            ),
            kind=e["kind"],
            label=e["label"],
            previous_value=e.get("previous", ""),
            new_value=e.get("current", ""),
            secondary=e.get("secondary", "") or "",
            secondary_tone=e.get("secondary_tone", "") or "",
            impact=e.get("impact", "medium"),
            difference=e.get("difference", "") or "",
            detected_at=now - timedelta(minutes=e.get("detected_minutes", 0)),
            metadata={
                "source_url": e.get("source_url", ""),
                "detected_at": e.get("detected_at", ""),
                "first_seen_at": e.get("first_seen_at", ""),
                "last_confirmed_at": e.get("last_confirmed_at", ""),
                "last_scanned": e.get("last_scanned", ""),
                "evidence": e.get("evidence", {}),
                "ai_note": e.get("ai_note", ""),
            },
        )


def _seed_own_products(workspace, products, now):
    """A small own-catalogue sample matched to canonical products (foundation)."""
    samples = [
        ("lego-castle-set", "OWN-LEGO-01", "29.99", "44.99", "47.99"),
        ("stem-robot-kit", "OWN-STEM-02", "22.00", "34.99", "37.99"),
        ("garden-water-table", "OWN-GARD-03", "38.00", "59.99", "62.99"),
    ]
    for slug, sku, cost, rrp, our in samples:
        OwnProduct.objects.create(
            workspace=workspace,
            product=products.get(slug),
            name=products[slug].name if slug in products else sku,
            own_sku=sku,
            cost=Decimal(cost),
            rrp=Decimal(rrp),
            our_price=Decimal(our),
        )


def _seed_team(workspace):
    """Add a couple of teammates (besides the owner) for a realistic team page.

    Users are reused across workspaces via get_or_create — a user may belong to
    many workspaces — so seeding multiple workspaces never collides on email.
    """
    from apps.accounts.models import User, WorkspaceMembership
    from apps.settings_app.data import TEAM_MEMBERS

    role_for = {1: WorkspaceMembership.Role.ADMIN}
    for idx, member in enumerate(TEAM_MEMBERS[1:], start=1):
        user = User.objects.filter(email__iexact=member["email"]).first()
        if user is None:
            first, _, last = member["name"].partition(" ")
            user = User.objects.create_user(
                email=member["email"], password=None, first_name=first, last_name=last
            )
        WorkspaceMembership.objects.get_or_create(
            user=user,
            workspace=workspace,
            defaults={"role": role_for.get(idx, WorkspaceMembership.Role.MEMBER)},
        )


def _seed_discovery(workspace):
    """Seed discovery candidates verbatim (preserves the Discovery UI values)."""
    from apps.discovery.data import DISCOVERY_CANDIDATES_SEED
    from apps.discovery.models import DiscoveryCandidate

    DiscoveryCandidate.objects.filter(workspace=workspace).delete()
    for c in DISCOVERY_CANDIDATES_SEED:
        DiscoveryCandidate.objects.create(
            workspace=workspace,
            name=c["name"],
            slug=c["slug"],
            domain=c["url"],
            website_url=f"https://{c['url']}",
            score=c["match"],
            tone=c.get("tone", "blue"),
            cluster=c.get("cluster", ""),
            status=c.get("status", "suggested"),
            reasons=c.get("why_match", []),
            catalogue_profile=c.get("catalogue_profile", {}),
        )


def _seed_alerts(workspace, now):
    """Seed alert rules + recent alerts (payload preserved for the UI)."""
    from datetime import timedelta

    from apps.alerts.data import ALERT_RULES, RECENT_ALERTS
    from apps.alerts.models import Alert, AlertRule

    Alert.objects.filter(workspace=workspace).delete()
    AlertRule.objects.filter(workspace=workspace).delete()

    by_seed_id = {}
    for r in ALERT_RULES:
        rule = AlertRule.objects.create(
            workspace=workspace,
            name=r["name"],
            type_group=r["type_group"],
            condition=r["condition"],
            competitors=r.get("competitors", "All competitors"),
            category=r.get("category", ""),
            frequency=r.get("frequency", "Immediate"),
            priority=r.get("priority", "medium"),
            enabled=r.get("active", True),
            channels=["in_app"],
            config={},
        )
        minutes = r.get("last_triggered_minutes")
        AlertRule.objects.filter(id=rule.id).update(
            created_at=timezone.make_aware(
                timezone.datetime.fromisoformat(r["created_at"])
            )
            if r.get("created_at")
            else now,
            last_triggered_at=(now - timedelta(minutes=minutes)) if minutes is not None else None,
        )
        by_seed_id[r["id"]] = rule

    for a in RECENT_ALERTS:
        rule = by_seed_id.get(a.get("rule_id"))
        payload = {k: v for k, v in a.items() if k not in ("id", "status")}
        if rule is not None:
            payload["rule_id"] = str(rule.pk)
        Alert.objects.create(
            workspace=workspace,
            rule=rule,
            status="viewed" if a.get("status") == "viewed" else "new",
            title=a.get("rule_name", ""),
            message=a.get("event", ""),
            payload=payload,
        )


def _seed_reports(workspace, now):
    """Seed generated reports + schedules."""
    from apps.reports.data import GENERATED_REPORTS, REPORT_SCHEDULES
    from apps.reports.models import Report, ReportSchedule
    from apps.reports.services import build_report_sections

    Report.objects.filter(workspace=workspace).delete()
    ReportSchedule.objects.filter(workspace=workspace).delete()

    status_map = {"generating": "generating", "ready": "ready", "attention": "ready"}
    for r in GENERATED_REPORTS:
        Report.objects.create(
            workspace=workspace,
            title=r["name"],
            report_type=r["type_id"],
            competitors=r.get("competitors", "All"),
            period=r.get("period", ""),
            status=status_map.get(r.get("status"), "ready"),
            generated_at=now,
            config={
                "type_title": r.get("type", r["type_id"]),
                "data_through": r.get("data_through", ""),
                "ai_analysis": True,
                "sections": build_report_sections(workspace, "Last 30 days"),
            },
        )
    for s in REPORT_SCHEDULES:
        ReportSchedule.objects.create(
            workspace=workspace,
            name=s["name"],
            report_type=s["type_id"],
            competitors=s.get("competitors", "All competitors"),
            frequency=s.get("frequency", "Every day"),
            run_time=s.get("time", "08:00"),
            enabled=s.get("active", True),
        )


def _seed_conversations(workspace):
    """Seed a few Ask AI conversations (owner-attributed)."""
    from apps.ai.data import CONVERSATION_HISTORY
    from apps.ai.models import Conversation

    Conversation.objects.filter(workspace=workspace).delete()
    owner = (
        workspace.memberships.filter(role="owner").select_related("user").first()
    )
    user = owner.user if owner else None
    # Insert in reverse so the first seed entry ends up most-recent (ordering by
    # -updated_at), matching the Phase 1 history order.
    for entry in reversed(CONVERSATION_HISTORY):
        Conversation.objects.create(workspace=workspace, user=user, title=entry["title"])


def seed_workspace(workspace, *, now=None):
    """Populate a workspace with the full demo dataset (idempotent)."""
    now = now or timezone.now()
    clear_workspace_data(workspace)
    competitors = _seed_competitors(workspace, now)
    products, primary_listing = _seed_products(workspace, competitors, now)
    _seed_history(workspace, primary_listing, now)
    _seed_change_events(workspace, competitors, products, primary_listing, now)
    _seed_own_products(workspace, products, now)
    _seed_team(workspace)
    _seed_discovery(workspace)
    _seed_alerts(workspace, now)
    _seed_reports(workspace, now)
    _seed_conversations(workspace)
    return workspace
