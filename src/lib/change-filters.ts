import { changeFilterOptions, type ChangeEvent } from "@/lib/changes-data"
import { categoryFromParam } from "@/lib/entities"
import { kindFromParam, rangeLabelFromParam } from "@/lib/product-filters"

/*
 * Pure filtering shared by the change events table and the page-level
 * Export button. The backend will eventually do this server-side
 * (GET /api/changes?...).
 */

export type ChangeFilters = {
  query: string
  competitor: string
  changeType: string
  category: string
  importance: string
  dateRange: string
  productSlug: string | null
}

export const defaultChangeFilters: ChangeFilters = {
  query: "",
  competitor: changeFilterOptions.competitors[0],
  changeType: "all",
  category: changeFilterOptions.categories[0],
  importance: "all",
  dateRange: "Today",
  productSlug: null,
}

const rangeMinutesByLabel: Record<string, number> = {
  Today: 24 * 60,
  "24 hours": 24 * 60,
  "7 days": 7 * 24 * 60,
  "30 days": 30 * 24 * 60,
}

const changeRangeLabelByParam: Record<string, string> = {
  today: "Today",
  "24h": "24 hours",
  "7d": "7 days",
  "30d": "30 days",
}

export function changeFiltersFromParams(
  params: URLSearchParams,
  competitorNameForSlug: (slug: string) => string | undefined
): ChangeFilters {
  const competitorSlug = params.get("competitor")
  const category = params.get("category")
  const rangeParam = params.get("range")
  return {
    query: params.get("q") ?? "",
    competitor:
      (competitorSlug && competitorNameForSlug(competitorSlug)) ??
      defaultChangeFilters.competitor,
    changeType: kindFromParam(params.get("type")),
    category:
      (category && categoryFromParam(category, changeFilterOptions.categories)) ??
      defaultChangeFilters.category,
    importance: ["high", "medium", "low"].includes(params.get("impact") ?? "")
      ? (params.get("impact") as string)
      : "all",
    dateRange:
      (rangeParam && changeRangeLabelByParam[rangeParam.toLowerCase()]) ??
      rangeLabelFromParam(rangeParam) ??
      defaultChangeFilters.dateRange,
    productSlug: params.get("product"),
  }
}

export const changeRangeParamByLabel: Record<string, string> = {
  Today: "today",
  "24 hours": "24h",
  "7 days": "7d",
  "30 days": "30d",
}

export function filterChanges(rows: ChangeEvent[], f: ChangeFilters): ChangeEvent[] {
  const q = f.query.trim().toLowerCase()
  const maxMinutes = rangeMinutesByLabel[f.dateRange]
  return rows.filter(
    (r) =>
      (!q ||
        r.product.name.toLowerCase().includes(q) ||
        r.competitor.toLowerCase().includes(q) ||
        r.category.toLowerCase().includes(q)) &&
      (f.competitor === defaultChangeFilters.competitor ||
        r.competitor === f.competitor) &&
      (f.changeType === "all" || r.kind === f.changeType) &&
      (f.category === defaultChangeFilters.category || r.category === f.category) &&
      (f.importance === "all" || r.impact === f.importance) &&
      (!f.productSlug || r.product.slug === f.productSlug) &&
      (maxMinutes === undefined || r.detectedMinutes <= maxMinutes)
  )
}

export function changesCsv(rows: ChangeEvent[]): {
  headers: string[]
  rows: (string | number)[][]
} {
  return {
    headers: [
      "Change",
      "Product",
      "SKU",
      "Competitor",
      "Category",
      "Previous",
      "Current",
      "Impact",
      "Detected",
    ],
    rows: rows.map((r) => [
      r.label,
      r.product.name,
      r.product.sku,
      r.competitor,
      r.category,
      r.previous,
      r.current,
      r.impact,
      r.detectedAt,
    ]),
  }
}
