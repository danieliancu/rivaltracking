# RivalTracking — Architecture

RivalTracking is a competitor-intelligence product: it monitors competitor
catalogues for price, stock, product and promotion changes, surfaces them as
dashboards, alerts and reports, and answers questions about them with AI.

This document describes the production architecture. **Phase 1 implements the
UI layer only**; the processing layer and most infrastructure are documented
here as the agreed direction but are explicitly **NOT implemented yet**.

## Phase 1 — UI layer (implemented)

Stack: **Python 3.11 · Django 5.2 · Django Templates · HTMX · Tailwind CSS v4
· Alpine.js (minimal) · Chart.js**. No React, no SPA framework, no JSON API
layer — server-rendered HTML with HTMX fragment swaps.

### Pages

| Page | Route | Django app |
|---|---|---|
| Overview | `/` | `apps.dashboard` |
| Competitors | `/competitors/`, `/competitors/<slug>/` | `apps.competitors` |
| Products | `/products/`, `/products/<slug>/` | `apps.products` |
| Changes | `/changes/` | `apps.changes` |
| Discovery | `/discovery/` | `apps.discovery` |
| Ask AI | `/ask-ai/` | `apps.ai` |
| Alerts | `/alerts/` | `apps.alerts` |
| Reports | `/reports/`, `/reports/<id>/` | `apps.reports` |
| Settings | `/settings/`, `/settings/<section>/` | `apps.settings_app` |
| (shell, search, mock store) | `/search/`, `/range/`, `/scan/`, `/dev/*` | `apps.core` |
| (auth placeholder) | — | `apps.accounts` |

### Application structure

```
app/
├── config/                 # settings split (base / local / production), urls, wsgi/asgi
├── apps/
│   ├── core/               # shell, shared component tags, mock store, search, formatting
│   └── <page apps>/        # each: urls.py, views.py, selectors.py, services.py, data.py
├── templates/              # single project-level tree; components/ = shared partials
└── static/                 # built Tailwind CSS, vendored JS, icons, mock images
```

Layering rules:

- **Views** are thin: parse request → call selectors/services → render a
  template or fragment.
- **Selectors** are pure reads (filtering, sorting, pagination, chart payload
  assembly).
- **Services** are mutations. Every service docstring records the future HTTP
  endpoint it stands in for (e.g. `POST /api/competitors/:id/scan`), carried
  over from the prototype's service layer.
- **Templates** own all presentation. Shared UI (badges, KPI cards, identity
  tiles, thumbnails, pagination, drawers, dialogs, charts) lives in
  `templates/components/` behind inclusion tags in
  `apps/core/templatetags/ui.py`, so variant→class maps have one source of
  truth.

### Mock data (Phase 1 only)

All data is deterministic seed data ported 1:1 from the prototype
(`apps/<app>/data.py`). A **session-backed copy-on-write store**
(`apps/core/mock/store.py`) gives every browser its own mutable demo
workspace: reads fall through to the immutable seeds until a collection is
first mutated, at which point it is copied into the Django session (DB-backed
sessions). "Reset demo data" in the account menu drops the session copy.

When the real backend arrives, `selectors.py`/`services.py` swap their store
calls for ORM queries and task dispatches; views and templates are unchanged.

### HTMX conventions

- **Addressable state** (table filters, sorting, pagination, chart ranges)
  uses the page's own URL: a filter `<form hx-get>` targets the table
  fragment and `hx-push-url` keeps the querystring shareable; the view
  returns only the fragment when `request.htmx.target` matches.
- **Ephemeral UI** (drawers, dialogs, search results, mutations) uses
  dedicated fragment routes rendering into persistent mounts
  (`#drawer-root`, `#modal-root`).
- **Toasts** are out-of-band swaps into `#toast-region`, appended to any
  mutation response.
- **Cross-fragment updates** (e.g. the sidebar unread-alerts badge) are
  out-of-band swaps included in the mutating response.
- CSRF is set once via `hx-headers` on `<body>`.

### JavaScript budget

- **HTMX** — all data fetching/updates.
- **Alpine.js** — purely client-side state only: menus, overlay open/close,
  staged-progress animations, bulk-select bars, transient "Saved" flashes.
- **Chart.js** (vendored) — the only rendering library; themed at runtime
  from the design-token CSS custom properties.

No bundler; all JS is vendored under `static/js/vendor/`.

## Phase 2 — data layer (implemented)

Phase 2 replaced the session mock store with PostgreSQL-ready ORM models,
authentication and multi-tenant workspaces. The `View → Selector / Service →
Template` layering is unchanged; the swap happened **inside** each app's
`selectors.py` / `services.py`, which now build the same dict/context shapes
from ORM rows, so templates were untouched.

### Identity & tenancy (`apps.accounts`)

- **`User`** — custom `AbstractUser`, email is the login field (no username);
  `apps.accounts.backends.EmailBackend` authenticates case-insensitively.
- **`Workspace`** + **`WorkspaceMembership`** (roles: owner/admin/member,
  extensible) + **`WorkspaceSettings`** (profile columns + JSON toggle
  sections). A user may belong to many workspaces.
- **`WorkspaceMiddleware`** sets `request.workspace` / `request.membership` from
  the session's active workspace (validated against membership). The app is
  gated by Django's `LoginRequiredMiddleware`; auth views opt out.

### Tenant isolation

Every business model has a `workspace` FK and a `WorkspaceManager` exposing
`.for_workspace(ws)`. Selectors filter by `request.workspace`; detail lookups
use `scoped_get_or_404` (`apps/core/scoping.py`) so foreign ids/slugs 404 (or
render the app's "not in your workspace" empty state) without leaking
existence. Services scope every write. `apps/accounts/tests/test_isolation.py`
proves reads, search and mutations never cross tenants.

### Data model

| App | Models |
|---|---|
| `accounts` | User, Workspace, WorkspaceMembership, WorkspaceSettings |
| `competitors` | Competitor (+ monitoring config, denormalised headline metrics) |
| `catalogue` | Product (canonical), ProductListing, OwnProduct, OwnListing, PriceSnapshot, StockSnapshot, Promotion |
| `changes` | ChangeEvent (typed, evidence + display strings in `metadata`) |
| `products` | WatchlistItem |
| `core` | WorkspaceDemoState (placeholder-app store) |

`Product ── ProductListing ── Competitor` supports one canonical product matched
to listings from many competitors; `OwnProduct`/`OwnListing` hold the customer's
own catalogue. Automated matching is Phase 3 — links are seed/manual for now.
Presentational-only fields (competitor headline counts, product tone/icon,
match confidence) are stored so the UI keeps its exact content; the Overview
KPIs/charts and the competitor/product/change KPIs are derived from ORM
aggregates over the Today/7D/30D window.

### Placeholder apps

Discovery, Ask AI, Alerts and Reports keep deterministic behaviour but their
user-mutable demo state is workspace-scoped in `WorkspaceDemoState` via
`apps/core/store.py::WorkspaceStore` (same get/mutate/replace/reset façade the
mock store had). Their real engines are Phase 3.

### Seeding

`apps/core/seed.py::seed_workspace` (and the `seed_demo` command) rebuild a
workspace from the same `apps/<app>/data.py` fixtures, anchoring timestamps to
"now" so relative-time labels render as before. It is idempotent. The test
suite seeds workspaces through the same code path.

## Processing layer — future phase (NOT implemented)

| Capability | Notes |
|---|---|
| Scraping | Fetch competitor catalogue/product pages on schedule |
| Normalisation | Clean raw HTML into canonical product records |
| Product matching | Cross-competitor product identity (the "Matched · N%" data) |
| Change detection | Diff successive snapshots into typed change events |
| Historical storage | Snapshot/event history powering charts and reports |
| AI analysis | Summaries, "why this matters" notes, Ask-AI answers |
| Alert engine | Evaluate alert rules against detected changes |
| Report generation | Compose period reports (incl. PDF export) |

Everything above is currently **mocked**: scans, discovery runs, report
generation and AI answers return deterministic data after a staged UI
animation.

## Infrastructure — future phase (NOT implemented)

- **Django** — application layer (present).
- **PostgreSQL** — primary database. Settings are PostgreSQL-ready
  (`config/settings/production.py` reads `DB_*` env vars); local bootstrap
  currently uses SQLite.
- **Redis** — cache + Celery broker. Not present.
- **Celery** — scheduled scans, scraping pipelines, alert evaluation, report
  builds. Not present.
- **Scraping workers / AI workers** — dedicated worker pools. Not present.
- **File/image storage** — real product images and generated report files
  (S3-compatible). Phase 1 ships local placeholder SVGs; the
  `{% product_thumbnail %}` component already renders real images when a
  product has one, with an icon-tile fallback.

## Phase 3 — intelligence engine (implemented)

Phase 3 adds the processing layer beneath the app: Celery + Redis, scheduled
crawling, deterministic scraping/extraction/normalisation, change detection,
matching, discovery, an AI abstraction, alert evaluation and report generation.
The `View → Selector / Service → Template` layering is unchanged; engine output
flows into the same selectors, so the UI is not redesigned.

### Processing pipeline

```
Competitor ─ Discovery ─ Fetcher(HTTP→browser*) ─ Extractor(JSON-LD→state→DOM→adapter→generic)
  → Normalizer → ProductListing (upsert, last_seen) → Price/Stock/Promotion snapshots
  → Change detection → ChangeEvent ─┬─ Matching → canonical Product → own-catalogue metrics
                                     ├─ Alert evaluation → Alert (in-app / email)
                                     └─ significance funnel → AI analysis (ChangeAnalysis)
Ask AI / Reports / Dashboard read the resulting real data.
```

### Async backbone (Celery + Redis)

`config/celery.py` defines one app with six routed queues — `scraping`,
`processing`, `matching`, `ai`, `alerts`, `reports` — so heavy scraping/AI never
starves lightweight work. Tasks take **IDs only** and re-resolve the workspace
and entities (never trust a passed object). Beat runs `dispatch_due_scans`
(enqueues due competitor scans, deduped by a cache lock + active-job check) and
`dispatch_due_schedules`. Tasks are idempotent; failures are isolated (a failed
page ≠ failed scan; a failed AI/alert ≠ rolled-back changes; `partially_failed`
status). Eager mode (inline, no broker) is the default locally/in tests.

### Scraping (`apps/scanning/scraping/`)

Pluggable `fetchers/` (HTTP default; optional Playwright), `extractors/`
(JSON-LD → DOM, structured before heuristics, **never AI**), `normalizers/`
(deterministic price/currency/stock/identifier), `adapters/`
(generic/shopify/woocommerce via a registry) and `discovery/` (sitemap +
product-URL patterns). The orchestrator applies per-domain rate limiting, a
`SCAN_MAX_PAGES` cap, `DiscoveredUrl` dedup and bounded `RawCapture` evidence,
and is fetcher-injectable so tests drive it from fixtures with no network.

### New models

`scanning`: ScanJob, DiscoveredUrl, RawCapture. `matching`: MatchResult.
`changes`: ChangeEvent (Phase 2) now written by detection. `ai`: Conversation,
Message, ChangeAnalysis. `alerts`: AlertRule, Alert. `reports`: Report,
ReportSchedule. `discovery`: DiscoveryCandidate. All workspace-scoped.

### Change detection, matching, discovery

Detection compares a listing's previous vs new normalised state and emits
idempotent ChangeEvents; **significance** (impact) is a separate module.
Matching links listings to a canonical Product deterministically
(GTIN → MPN+brand → SKU → title similarity), auto-merging high-confidence
matches. Discovery scores candidates by catalogue overlap (a search/links
provider is a documented seam).

### AI

`apps/ai/providers/` — an `AIProvider` interface with a deterministic
`StubProvider` (default, offline) and an `OpenAIProvider` (opt-in). AI runs on
the `ai` queue over **structured events/facts only** (never raw pages): a
significance funnel selects a small set of ChangeEvents for `analyse_change`,
and Ask AI answers via workspace-scoped retrieval tools (`apps/ai/tools.py`) so
answers can never cross tenants.

### Scalability

Changes filtering/sorting/pagination run in the database; global search uses
PostgreSQL trigram ranking (icontains on SQLite) over name/SKU/GTIN. Indexes
cover workspace+time, competitor+time, listing+captured_at, event type,
active/status and product identifiers.

### Deferred (seams in place)

Real Playwright rendering, image thumbnail/object-storage wiring, PDF export,
semantic/embedding matching, proxy pool, Stripe/plan enforcement. Live crawling
is validated against fixtures — tests never hit the network or live AI.

## Phase 3.5 — usable intelligence loop & no production mock data

Phase 3.5 closes the last gap between the engine and a real first-time user, and
removes every remaining invented business fact from production. The layering and
UI are unchanged; the same `View → Selector → Template` path now renders **only**
workspace-scoped ORM data — rich for the seeded demo, empty for a fresh account.

### Own catalogue (the customer's own store)

- **`catalogue.OwnCatalogueSource`** (one per workspace × source_type
  `website`/`csv`/`api`): holds `website_url`/`domain`, `status`, `last_import_at`,
  `products_found`, `errors_count`, `error_summary` and a `config` JSON.
- **`apps/catalogue/importing.py`** reuses the Phase 3 scraping pipeline against
  the *own* site: `select_adapter` + `adapter.discover(source)` (duck-typed on
  `.website_url`/`.domain`) + `orchestration.scrape_url` (already
  Competitor-agnostic) → normalise → upsert `OwnProduct`/`OwnListing`
  (channel `website`). It runs on the `processing` queue
  (`apps/catalogue/tasks.py::import_catalogue`) and is fetcher-injectable for
  tests. **The own site is never a `Competitor`.**
- **`apps/catalogue/csv_import.py`** auto-maps headers, validates rows, and
  upserts the same models (channel `csv`). **`apps/catalogue/api.py::ingest`** is
  a token-authed (`X-Api-Token` on `WorkspaceSettings`) upsert seam at
  `POST /catalogue/api/ingest/`.
- Every imported `OwnProduct` is matched with
  `apps/matching/engine.py::match_own_product` (GTIN → MPN+brand → SKU → title);
  when nothing matches it creates the canonical `Product` so later competitor
  listings converge onto it.

### Comparison (deterministic, no AI)

`apps/catalogue/selectors.py` derives, per matched product, our price vs the
competitor market (lowest/highest/median/average, `position`,
`diff_vs_lowest_pct`, in-stock competitors), plus workspace-level
`catalogue_gaps` (competitors sell, we don't), `unmatched_own_products` (we sell,
competitors don't) and an `own_position_summary`. These feed Overview, Products,
Reports and the Ask AI market-position path — all zero/empty for a new workspace.

### No production mock data

For a normal workspace, no selector emits invented facts. The Phase 1
`apps/*/data.py` business corpora are no longer imported by production code
(reports KPIs & detail body, products/changes/alerts charts, the competitors
activity feed, discovery reference profile, AI-insight prose and Ask AI's canned
answers were all replaced by ORM-derived selectors). `StubProvider.answer_question`
now answers from real workspace facts or returns a *"not enough data collected
yet"* card — it never fabricates business facts. Genuinely-static UI config
(labels, cluster names, report-type library, suggested prompts) stays as
constants with no company names or counts. Demo richness is produced solely by
`seed_demo` populating real rows, so the derive-from-ORM selectors render it.

Guardrails: `apps/accounts/tests/test_empty_workspace.py` asserts a fresh signup
renders every page with zero demo data and the no-data Ask AI card;
`apps/core/tests/test_no_mock_dependency.py` asserts production modules import no
legacy business seeds and contain no demo company names;
`apps/catalogue/tests/test_e2e.py` drives connect → import → scan → match →
real price position offline.

### Discovery & live validation

Discovery generates candidates only through a pluggable `SearchProvider` seam
(stub returns none → empty state); **add-competitor-by-URL** is the primary path
and is surfaced from the empty state. Scoring uses real catalogue/brand/category
overlap. The scraper is validated against real sites with
`python manage.py scan_url <url>` (respects `robots.txt`, no CAPTCHA bypass);
the automated suite never hits the network.
