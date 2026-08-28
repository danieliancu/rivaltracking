import type { MonitoringStatus } from "@/components/shared/status-badge"

/*
 * Mock data shaped like the future API responses from the Python backend
 * (Django + Celery + change detection). Presentation components must not
 * hard-code any of these values.
 */

export type CompetitorRow = {
  slug: string
  name: string
  url: string
  market: string
  products: number | null
  changesToday: number | null
  priceDrops: number | null
  priceIncreases: number | null
  stockChanges: number | null
  lastScan: string
  /* Numeric mirror of lastScan for sorting; the backend will return real
     timestamps instead. */
  lastScanMinutes?: number
  status: MonitoringStatus
  /* Business-friendly note shown under the status (never technical). */
  note?: string
  addedAt: string
}

export const competitorRows: CompetitorRow[] = [
  {
    slug: "toyworld-co-uk",
    name: "ToyWorld.co.uk",
    url: "toyworld.co.uk",
    market: "UK Toys",
    products: 2438,
    changesToday: 67,
    priceDrops: 64,
    priceIncreases: 18,
    stockChanges: 31,
    lastScan: "12 min ago",
    lastScanMinutes: 12,
    status: "healthy",
    addedAt: "2026-03-02",
  },
  {
    slug: "playnest-co-uk",
    name: "PlayNest.co.uk",
    url: "playnest.co.uk",
    market: "UK Toys",
    products: 1984,
    changesToday: 31,
    priceDrops: 21,
    priceIncreases: 7,
    stockChanges: 14,
    lastScan: "26 min ago",
    lastScanMinutes: 26,
    status: "healthy",
    addedAt: "2026-04-18",
  },
  {
    slug: "happytoyhouse-com",
    name: "HappyToyHouse.com",
    url: "happytoyhouse.com",
    market: "UK Toys",
    products: 2103,
    changesToday: 19,
    priceDrops: 8,
    priceIncreases: 4,
    stockChanges: 7,
    lastScan: "1h ago",
    lastScanMinutes: 60,
    status: "attention",
    note: "Some product pages could not be scanned.",
    addedAt: "2026-05-30",
  },
  {
    slug: "littlemindstoys-co-uk",
    name: "LittleMindsToys.co.uk",
    url: "littlemindstoys.co.uk",
    market: "UK Toys",
    products: 2221,
    changesToday: 4,
    priceDrops: 2,
    priceIncreases: 1,
    stockChanges: 1,
    lastScan: "Scanning now",
    lastScanMinutes: 0,
    status: "scanning",
    addedAt: "2026-07-11",
  },
]

export const competitorKpis = [
  { id: "competitors", label: "Monitored competitors", value: "4", tone: "info" },
  { id: "products", label: "Products monitored", value: "8,746", tone: "info" },
  { id: "changes", label: "Changes today", value: "121", tone: "success" },
  { id: "attention", label: "Attention required", value: "2", tone: "warning" },
] as const

export type ActivityTone = "success" | "info" | "warning" | "destructive" | "purple"

export type ActivityEvent = {
  company: string
  event: string
  time: string
  kind: "prices-down" | "new-products" | "pages-unavailable" | "out-of-stock" | "promotion"
}

export const activityEvents: ActivityEvent[] = [
  { company: "ToyWorld.co.uk", event: "64 prices reduced", time: "12 min ago", kind: "prices-down" },
  { company: "PlayNest.co.uk", event: "11 new products discovered", time: "26 min ago", kind: "new-products" },
  { company: "HappyToyHouse.com", event: "7 product pages unavailable", time: "1h ago", kind: "pages-unavailable" },
  { company: "ToyWorld.co.uk", event: "31 products went out of stock", time: "2h ago", kind: "out-of-stock" },
  { company: "LittleMindsToys.co.uk", event: "New promotion detected in Educational Toys", time: "3h ago", kind: "promotion" },
]

export const discoverySuggestions = [
  { name: "BrightKidsPlay.com", match: 82, tone: "orange" },
  { name: "ToyCorner.co.uk", match: 79, tone: "blue" },
  { name: "KidsPlayStore.co.uk", match: 76, tone: "teal" },
] as const

export const monitoringHealth = {
  healthy: 3,
  attention: 1,
  lastSuccessfulScan: "12 minutes ago",
  nextScheduledScan: "in 48 minutes",
}

/* Stages simulated by the Add Competitor onboarding flow. */
export const scanStages = [
  "Detecting website",
  "Discovering catalogue",
  "Finding products",
  "Creating initial snapshot",
  "Monitoring enabled",
] as const

export const addedCompetitorResult = {
  name: "ToyPlanet.co.uk",
  slug: "toyplanet-co-uk",
  url: "toyplanet.co.uk",
  products: 1824,
  categories: 31,
}
