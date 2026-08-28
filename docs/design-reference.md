# Design reference — React prototype → Django mapping

The React prototype under `prototype-react/` is the visual and interaction
spec. This document maps each prototype module to its Django equivalent and
records the conscious deviations.

## Design system

| Prototype | Django |
|---|---|
| `src/styles.css` (Tailwind v4 `@theme inline`, oklch tokens, `bg-ai-subtle` utility) | `app/static/src/styles.css` — same file with `@source` repointed at `templates/` and `apps/`; built to `app/static/css/app.css` |
| Inter via Google Fonts | same `<link>` in `templates/base.html` |
| lucide-react icons | vendored lucide SVGs in `app/static/icons/lucide/` + `{% icon %}` tag (inline SVG, `currentColor`) |
| shadcn/ui primitives (Button, Card, Badge, Table, …) | plain markup carrying the same Tailwind class strings; shared variants live in `apps/core/templatetags/ui.py` |
| Recharts (`components/ui/chart.tsx`) | Chart.js v4 (vendored) via `{% chart %}` + `static/js/charts.js`, themed from the CSS custom properties |
| sonner toasts | `templates/partials/toast.html` OOB-swapped into `#toast-region` (same bottom-right look, icons, timing) |
| Radix Sheet / Dialog / AlertDialog | `templates/components/sheet_shell.html` / `dialog_shell.html` (Alpine overlay + focus trap), HTMX-loaded into `#drawer-root` / `#modal-root` |
| Radix DropdownMenu / Popover | Alpine `menu()` pattern with the shadcn panel classes |
| Radix Select (filter bars) | **styled native `<select>`** via `{% filter_select %}` — identical closed appearance; the open panel is browser-native (accepted trade-off) |
| Radix Switch | styled checkbox (`peer` CSS) |
| Radix Tabs | server-rendered links (URL/tab param) or HTMX fragment buttons for chart-local tabs |
| `useIsMobile()` JS breakpoint (mobile card lists) | CSS-only `md:hidden` / `hidden md:block` twin rendering |

## Shell

| Prototype | Django |
|---|---|
| `App.tsx` providers + routes | `config/urls.py` + per-app `urls.py`; global state → session (date range, selected competitor) |
| `components/ui/sidebar.tsx` + `dashboard/app-sidebar.tsx` | `templates/partials/sidebar.html` (+`sidebar_content.html`, `sidebar_badge.html`); desktop fixed 16rem rail, Alpine offcanvas <768px |
| `dashboard/dashboard-header.tsx` | `templates/partials/header.html` (search palette → `GET /search/` fragment; range tabs → `POST /range/` + `range:changed` event; Run Scan → `POST /scan/`; account menu; sign-out AlertDialog) |
| `lib/workspace-store.tsx` (mock backend state) | `apps/core/mock/store.py` — session copy-on-write store over `apps/<app>/data.py` seeds |
| `lib/ui-store.tsx` (dateRange, selectedCompetitor, scanning) | Django session keys + HTMX indicators |
| `lib/alerts-store.tsx` (unreadCount) | computed in `apps/core/context_processors.py`; OOB badge swaps on mark-read |
| `services/*.ts` (mockOk latency + endpoint comments) | `apps/<app>/services.py` (no artificial latency; endpoint comments preserved in docstrings) |

## Shared components (`src/components/shared/`)

| Prototype | Django (`{% load ui %}`) |
|---|---|
| `kpi-card.tsx` | `{% kpi_card icon tone value label href %}` |
| `status-badge.tsx` | `{% status_badge status %}` |
| `change-badge.tsx` (14 kinds) | `{% change_badge kind label %}` |
| `stock-badge.tsx` | `{% stock_badge in_stock %}` |
| `impact-badge.tsx` | `{% impact_badge impact %}` |
| `change-value.tsx` | `{% change_value previous current secondary tone %}` |
| `competitor-identity.tsx` (hash-toned tile) | `{% competitor_identity name url %}` (same 32-bit hash) |
| `product-identity.tsx` | `{% product_identity product=… href=… %}` |
| `empty-state.tsx` | `{% empty_state heading text icon action_label action_href %}` |
| `ai-insight-card.tsx` | `templates/components/ai_insight_card.html` include |
| `company-discovery-row.tsx` | `templates/components/company_discovery_row.html` |
| — (new in Django) | `{% product_thumbnail product size %}` — real-image support with icon-tile fallback |

## Pages

| Prototype page / components | Django templates (under `app/templates/`) |
|---|---|
| `pages/overview.tsx`, `dashboard/kpi-cards|ai-summary|analytics-charts|changes-table|discoveries` | `dashboard/overview.html` + `dashboard/partials/` (metrics, competitor_pill, changes_card, ai_summary_body) |
| `pages/competitors.tsx`, `competitors/*` | `competitors/index.html` + `competitors/partials/` (table, add dialog with staged scan, monitoring drawer, health, activity) |
| `pages/competitor-details.tsx` | `competitors/detail.html` (tabs reuse the products table and changes card partials) |
| `pages/products.tsx`, `products/*` | `products/index.html` + `products/partials/` (table, filters, compare drawer) |
| `pages/product-details.tsx` | `products/detail.html` |
| `pages/changes.tsx`, `changes/*` | `changes/index.html` + `changes/partials/` (table, patterns, activity chart, detail_drawer, snapshot_panel) |
| `pages/discovery.tsx`, `discovery/*` | `discovery/index.html` + `discovery/partials/` (clusters, rows, run dialog, why-match & compare drawers) |
| `pages/ask-ai.tsx`, `ask-ai/*` | `ai/index.html` + `ai/partials/` (history, thread, composer, context bar, `blocks/` per response block) |
| `pages/alerts.tsx`, `alerts/*` | `alerts/index.html` + `alerts/partials/` (rules table, recent table, rule dialog, alert drawer, charts) |
| `pages/reports.tsx`, `pages/report-details.tsx`, `reports/*` | `reports/index.html`, `reports/detail.html` + `reports/partials/` |
| `pages/settings.tsx`, `settings/*` incl. `primitives.tsx` | `settings_app/index.html` + `settings_app/partials/` (`sections/` ×8, primitives as partials) |
| `pages/not-found.tsx` | `templates/404.html` (preview at `/dev/404/` in DEBUG) |

## Interaction translations

| React mechanism | Django/HTMX mechanism |
|---|---|
| Client filter state + `setSearchParams` | filter `<form hx-get hx-push-url>` → table fragment; same query params |
| `paginate()` client slice (PAGE_SIZE 8) | `apps/core/selectors.paginate` + `{% pagination %}` prev/next |
| Drawer `useState` + Radix Sheet | `GET …/drawer/` fragment → `#drawer-root` |
| Dialog phases with `setTimeout` stage theatre | POST performs the mutation, response renders the staged fragment; Alpine `stagedProgress()` animates and fires a body event that tables listen for |
| Router `navigate(state)` deep links (create alert / create report / Ask AI context) | query-param deep links (`/alerts?create=1&…`, `/reports?create=…`, `/ask-ai?prompt=…`) |
| Client CSV Blob download (`lib/csv.ts`) | plain Django CSV `HttpResponse` endpoints |
| sonner `toast.*` calls | OOB toast include on the mutation response (same copy) |
| 600 ms fake skeletons | `hx-indicator` skeletons during real fragment swaps |

## Conscious deviations

1. **Native select panels** — filter dropdowns open the OS/browser panel
   rather than a Radix-styled popover. Closed state is pixel-matched.
2. **Chart.js instead of Recharts** — same chart types, colors, dashes,
   heights and disabled animations; minor differences in tooltip typography
   and curve interpolation.
3. **Product thumbnails added** — the prototype had no product images.
   Phase 1 adds `{% product_thumbnail %}` (table sm, drawer md, detail lg,
   lazy-loaded, aspect-square) with generated placeholder SVGs and the
   prototype's icon tile as the missing-image fallback. Icon tiles are kept
   in dense cross-entity contexts (changes tables, search) as in the
   prototype.
4. **No artificial latency** — the prototype's `mockOk(…, ms)` delays are
   dropped; staged dialogs keep their timed animations because they are part
   of the designed UX.
5. **Alert rules store structured fields** (`trigger`, `operator`,
   `threshold`) instead of reverse-parsing the display condition string.
6. **Relative times** are canonical integer minutes with display strings
   kept from the fixtures; new mutations derive strings via
   `apps/core/format.py`.
