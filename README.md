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

# 2. Database (SQLite locally) — create the schema
python manage.py migrate

# 3. Seed a demo workspace (user, competitors, products, history, events)
python manage.py seed_demo

# 4. Run
python manage.py runserver
```

Open http://127.0.0.1:8000/. The app is **login-gated**. Either click
**Enter the demo** on the sign-in page, or use the seeded credentials:

- **Email:** `demo@rivaltracking.com`
- **Password:** `demo-rivaltracking`

You can also **create a new account** (Sign up), which provisions a fresh empty
workspace you own. No environment variables are required locally (see
`app/.env.example` for the production set).

Data is now stored in a real relational database (Phase 2). Each account
belongs to one or more **workspaces**, and every competitor, product, price/
stock snapshot, promotion and change event is scoped to a workspace — users
never see another workspace's data. The **Reset demo data** action (avatar
menu) re-seeds the current workspace.

`python manage.py createsuperuser` gives you access to the Django admin at
`/admin/` for inspecting users, workspaces, competitors, products, listings,
snapshots, promotions and change events.

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

The suite renders every page and fragment route against a seeded workspace and
covers authentication, workspace membership, **tenant isolation**, competitor/
product/listing relationships, price/stock history, change events, selectors,
HTMX fragments, pagination/filtering and the seed command.

## Running the processing engine locally (Phase 3)

The engine (scraping, change detection, matching, AI, alerts, reports) runs on
Celery. Locally, tasks execute **eagerly** (inline, no broker) and live scraping
is **off** by default, so `runserver` alone exercises everything against seeded
data and the test fixtures — no Redis needed.

To run the real asynchronous engine locally, start Redis and workers:

```bash
# Terminal 1 — web
CELERY_TASK_ALWAYS_EAGER=0 python manage.py runserver
# Terminal 2 — worker (all queues)
CELERY_TASK_ALWAYS_EAGER=0 celery -A config worker -l info \
  -Q scraping,processing,matching,ai,alerts,reports
# Terminal 3 — beat (scheduler; never run inside the web process)
CELERY_TASK_ALWAYS_EAGER=0 celery -A config beat -l info
```

Set `SCANNING_LIVE=1` to fetch real competitor sites; `AI_PROVIDER=openai` +
`OPENAI_API_KEY` to use OpenAI (default is the offline deterministic stub).
Browser (JS) rendering is optional: build `requirements/browser.txt`, run
`playwright install chromium`, and set `BROWSER_ENABLED=1` on a dedicated worker.

### Pipeline

```
Competitor ─ Discovery ─ Fetcher(HTTP→browser*) ─ Extractor(JSON-LD→DOM→adapter)
  → Normalizer → ProductListing → Price/Stock/Promotion snapshots
  → Change detection → ChangeEvent ─┬─ Matching → canonical Product → own-price metrics
                                     ├─ Alert evaluation → Alert (in-app/email)
                                     └─ significance funnel → AI analysis (ChangeAnalysis)
Ask AI / Reports / Overview read the resulting real data.
```

Deterministic before AI, HTTP before browser, structured data before DOM,
events before AI — AI only interprets structured results.

## Deploying with PostgreSQL (Coolify)

The Phase 1 demo ran on SQLite. To run Phase 2 against a Coolify PostgreSQL
service, add a Postgres resource and set these environment variables on the app:

```
DJANGO_SETTINGS_MODULE=config.settings.demo   # or config.settings.production
SECRET_KEY=<a long random string>
ALLOWED_HOSTS=your-demo-host
CSRF_TRUSTED_ORIGINS=https://your-demo-host
DB_NAME=<postgres db>
DB_USER=<postgres user>
DB_PASSWORD=<postgres password>
DB_HOST=<postgres service host>
DB_PORT=5432
```

`config.settings.demo` uses PostgreSQL automatically when `DB_HOST` is set and
otherwise falls back to the committed SQLite file, so the existing demo keeps
working if you deploy without a database. On first deploy (and after model
changes) run, inside the container:

```bash
python manage.py migrate
python manage.py seed_demo
```

WhiteNoise serves the built static files (`collectstatic` runs in the
Dockerfile).

### Phase 3 services on Coolify

Deploy five processes from the same image (Redis + Postgres as managed
resources):

| Service | Command |
|---|---|
| web | `gunicorn config.wsgi:application --bind 0.0.0.0:8000` (Dockerfile also runs `migrate`) |
| worker | `celery -A config worker -l info -Q scraping,processing,matching,ai,alerts,reports` |
| beat | `celery -A config beat -l info` (never in the web process) |
| redis | managed Redis resource |
| postgres | managed PostgreSQL resource |

An optional `browser-worker` (built from `requirements/browser.txt`, `BROWSER_ENABLED=1`,
`-Q scraping`) handles JS-rendered pages. Extra env for the engine:

```
REDIS_URL=redis://<redis-host>:6379/0
CELERY_TASK_ALWAYS_EAGER=0
SCANNING_LIVE=1
AI_PROVIDER=openai            # or leave unset for the deterministic stub
OPENAI_API_KEY=sk-...
CELERY_WORKER_CONCURRENCY=4   # tune to the VPS; browser workers stay small
```

After deploy: `python manage.py migrate` (automatic), then `python manage.py
seed_demo` once for the demo workspace. Recommended minimum: 1 web, 1 worker
(concurrency 2-4), 1 beat, Redis, Postgres; scale workers per queue as scan
volume grows. Health check: `GET /accounts/login/` (200).

## Implementation status (Phase 3 — intelligence engine)

Phase 3 added the real processing engine beneath the app:

- **Celery + Redis** with six routed queues (scraping/processing/matching/ai/
  alerts/reports) and a beat scheduler; eager (no-broker) mode for local/tests.
- **Scan engine**: ScanJob + a pluggable HTTP fetcher → JSON-LD/DOM extractor →
  deterministic normaliser → ProductListing upsert, with sitemap/pattern URL
  discovery, per-domain rate limiting, evidence capture and safe removal.
- **Change detection** → idempotent ChangeEvents (+ separate significance);
  **product matching** (GTIN→MPN→SKU→title) with confidence/method; **own-price
  metrics**; **competitor discovery** by catalogue overlap.
- **AI** provider abstraction (OpenAI + deterministic stub default): change
  analysis on a significance funnel, Ask AI over workspace-scoped retrieval
  tools, persisted conversations.
- **Alert evaluation** (in-app + email) and **report generation** (deterministic
  metrics + AI narrative) from real data; DB-level changes filtering + trigram
  search; scan-health observability.

Everything stays workspace-isolated; Playwright/PDF/image-storage/embeddings are
scaffolded seams (see `docs/architecture.md`).

## Implementation status (Phase 2 — product foundation)

Phase 2 replaced the Phase 1 session mock store with a real relational model:

- **Accounts & auth**: custom email-login `User`, sign-up / login / logout /
  password-reset, login-gated app, one-click demo sign-in.
- **Workspaces**: `Workspace`, `WorkspaceMembership` (owner/admin/member),
  `WorkspaceSettings`; a user may belong to many workspaces; every business
  object is workspace-scoped with enforced tenant isolation.
- **Catalogue**: canonical `Product`, per-competitor `ProductListing`, customer
  `OwnProduct`/`OwnListing`, and `PriceSnapshot`/`StockSnapshot`/`Promotion`
  history; `Competitor`; `ChangeEvent`; `WatchlistItem`.
- **DB-backed pages**: Overview (ORM-derived KPIs + charts), Competitors,
  Products, Changes, global Search and Settings read/write the ORM.
- **Placeholder apps** (Discovery, Ask AI, Alerts, Reports) keep deterministic
  behaviour but are workspace-scoped via a `WorkspaceDemoState`-backed store —
  their real engines are Phase 3.
- **Ops**: Django admin for all models, `seed_demo` management command,
  PostgreSQL-ready settings.

## Phase 1 UI (still intact)

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
