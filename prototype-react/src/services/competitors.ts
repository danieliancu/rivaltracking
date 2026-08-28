import { mockOk } from "@/services/mock"
import { slugify } from "@/lib/entities"
import type { CompetitorRow } from "@/lib/competitors-data"

export type ScanResult = {
  competitorName: string
  newChanges: number
}

/** Future: POST /api/competitors/:id/scan → { newChanges } (Celery task). */
export function runScan(competitorName: string): Promise<ScanResult> {
  return mockOk({ competitorName, newChanges: 12 }, 1800)
}

/** Future: POST /api/competitors → CompetitorRow (crawler + initial snapshot). */
export function addCompetitor(url: string): Promise<CompetitorRow> {
  const host = url.replace(/^https?:\/\//, "").replace(/^www\./, "").replace(/\/.*$/, "")
  const name = host
    .split(".")[0]
    .replace(/[-_]/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .replace(/\s+/g, "")
    .concat(host.includes(".") ? host.slice(host.indexOf(".")) : "")
  return mockOk(
    {
      slug: slugify(host),
      name,
      url: host,
      market: "UK Toys",
      products: 1824,
      changesToday: null,
      priceDrops: null,
      priceIncreases: null,
      stockChanges: null,
      lastScan: "Just now",
      status: "initialising",
      note: "Initial snapshot in progress — changes appear after the next scan.",
      addedAt: new Date().toISOString().slice(0, 10),
    },
    400
  )
}

/** Future: POST /api/competitors/:id/pause */
export function pauseCompetitor(slug: string): Promise<{ slug: string }> {
  return mockOk({ slug }, 300)
}

/** Future: POST /api/competitors/:id/resume */
export function resumeCompetitor(slug: string): Promise<{ slug: string }> {
  return mockOk({ slug }, 300)
}

/** Future: DELETE /api/competitors/:id (stops monitoring; data removal is separate). */
export function removeCompetitor(slug: string): Promise<{ slug: string }> {
  return mockOk({ slug }, 300)
}

export type CompetitorMonitoringConfig = {
  frequency: string
  trackPrices: boolean
  trackStock: boolean
  trackProducts: boolean
  trackPromotions: boolean
}

/** Future: PATCH /api/competitors/:id (monitoring configuration only —
 *  actual scheduling lives in Django/Celery, never in the frontend). */
export function saveMonitoringConfig(
  slug: string,
  config: CompetitorMonitoringConfig
): Promise<CompetitorMonitoringConfig> {
  void slug
  return mockOk(config, 500)
}
