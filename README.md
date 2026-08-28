# RivalTracking

Competitor intelligence for e-commerce: monitor competitor catalogues for
price, stock, product and promotion changes; get dashboards, alerts, reports
and AI answers about what moved.

## Repository layout

| Path | Role |
|---|---|
| `prototype-react/` | **Design & UX prototype only** (React + Vite). Read-only visual reference — not part of the production stack. |
| `app/` | **Production application**: Django 5.2 + Django Templates + HTMX + Tailwind CSS v4 + minimal Alpine.js. |
| `docs/` | Architecture and design-mapping documentation. |

React is **not** used in the production application. The prototype exists so
the Django UI can be rebuilt faithfully against it; treat it as a spec, not
as code to import.

## Running the Django app locally

Requirements: Python 3.11+, Node 20+ (build-time only, for Tailwind).

```bash
cd app

# 1. Python environment
python -m venv .venv
.venv\Scripts\activate            # Windows (source .venv/bin/activate elsewhere)
pip install -r requirements/local.txt

# 2. Database (SQLite; used only for sessions in Phase 1)
python manage.py migrate

# 3. Run
python manage.py runserver
```

Open http://127.0.0.1:8000/. No environment variables are required locally
(see `app/.env.example` for the production set).

The UI is populated by deterministic mock data. Anything you change (add a
competitor, create an alert, save settings…) is stored in **your session
only** — use the avatar menu → **Reset demo data** to restore the seed state.

## Running Tailwind locally

The built stylesheet (`app/static/css/app.css`) is committed, so Node is only
needed when editing styles/templates:

```bash
cd app
npm install
npm run dev     # watch mode — rebuilds app.css as templates change
npm run build   # minified production build
```

The design system lives in `app/static/src/styles.css` (Tailwind v4,
CSS-first tokens ported from the prototype).

## Tests

```bash
cd app
python -m pytest
```

The suite renders every page and fragment route against the mock data.

## Implementation status (Phase 1)

Implemented — full UI with mock data:

- Overview dashboard (KPIs, AI summary, trend/category/stock charts, recent
  changes, discoveries) with the global Today/7D/30D range switch
- Competitors (table, add-competitor staged dialog, pause/resume/remove,
  monitoring-settings drawer) and competitor details (tabs)
- Products (filterable/sortable/paginated table with URL-synced filters,
  compare drawer, watchlist, CSV export, thumbnails) and product details
- Changes (filter bar incl. 14 change types, saved views, patterns, activity
  charts, change-detail drawer with evidence snapshots, CSV export)
- Discovery (clusters, match evidence drawers, staged discovery run)
- Ask AI (structured answer cards over a canned response corpus,
  conversations, context chips, suggested questions)
- Alerts (rules table, recent alerts with unread tracking, create/edit rule
  dialog, detail drawer, activity charts)
- Reports (library, generated reports, schedules, staged generation dialog,
  full report detail page, CSV export)
- Settings (workspace, monitoring, notifications, AI, reports, team, data &
  privacy incl. danger zone, billing)

Mocked on purpose (deterministic data, no external calls):

- All competitor/product/change/discovery data and counts
- Scan runs, discovery runs and report generation (staged UI animations over
  instant mock mutations)
- AI summaries, notes and Ask-AI answers (regex-matched canned corpus)
- Product thumbnails (generated placeholder SVGs; real images slot into the
  same component)

Deferred to later phases (intentionally not built):

- Real scraping, normalisation, product matching and change detection
- Celery/Redis job infrastructure and scheduled scans
- Real AI processing and external AI APIs
- Alert delivery channels (email/Slack) and the alert evaluation engine
- PDF report generation; report scheduling backend
- Billing integration, authentication and multi-user workspaces
- PostgreSQL in production (settings are ready; local bootstrap is SQLite)

See `docs/architecture.md` for the full picture and
`docs/design-reference.md` for the React→Django mapping.
