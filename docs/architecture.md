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
