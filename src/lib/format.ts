import type { ScanResult } from "@/services/competitors"

/* Shared copy so the header Run Scan and the competitor-row scan action
   show identical feedback. */
export function scanToastMessage(result: ScanResult): {
  title: string
  description: string
} {
  return {
    title: "Scan complete",
    description: `${result.newChanges} new changes detected across ${result.competitorName}.`,
  }
}

export type PageSlice<T> = {
  slice: T[]
  page: number
  pageCount: number
  from: number
  to: number
  total: number
}

export function paginate<T>(rows: T[], page: number, pageSize = 10): PageSlice<T> {
  const total = rows.length
  const pageCount = Math.max(1, Math.ceil(total / pageSize))
  const safePage = Math.min(Math.max(1, page), pageCount)
  const start = (safePage - 1) * pageSize
  const slice = rows.slice(start, start + pageSize)
  return {
    slice,
    page: safePage,
    pageCount,
    from: total === 0 ? 0 : start + 1,
    to: start + slice.length,
    total,
  }
}

/* Minutes-ago thresholds for the Today / 7D / 30D range filters. */
export const rangeMinutes = { today: 24 * 60, "7d": 7 * 24 * 60, "30d": 30 * 24 * 60 } as const
