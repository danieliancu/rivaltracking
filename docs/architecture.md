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
