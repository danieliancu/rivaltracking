import { filterOptions, type ProductRow, type SortValue } from "@/lib/products-data"
import { categoryFromParam } from "@/lib/entities"

/*
 * Pure filtering shared by the products table and the page-level Export
 * button so both always operate on the same filtered set. The backend will
 * eventually do this server-side (GET /api/products?...).
 */

export type ProductFilters = {
  query: string
  competitor: string
  category: string
  changeType: string
  stock: string
  dateRange: string
}

export const defaultProductFilters: ProductFilters = {
  query: "",
  competitor: filterOptions.competitors[0],
  category: filterOptions.categories[0],
  changeType: "all",
  stock: "all",
  dateRange: "30 days",
}

/* Query-param tokens (spec-level, e.g. "price-decrease") → ChangeKind. */
const kindByParam: Record<string, string> = {
  new: "new",
  "price-decrease": "drop",
  drop: "drop",
  "price-increase": "increase",
  increase: "increase",
  "out-of-stock": "oos",
  oos: "oos",
  "back-in-stock": "back",
  back: "back",
  removed: "removed",
  "promotion-started": "promo",
  promo: "promo",
  name: "name",
  category: "category",
}

export function kindFromParam(param: string | null): string {
  if (!param) return "all"
  return kindByParam[param.toLowerCase()] ?? "all"
}

const rangeLabelByParam: Record<string, string> = {
  today: "Today",
  "7d": "7 days",
  "30d": "30 days",
}

export function rangeLabelFromParam(param: string | null): string | undefined {
  return param ? rangeLabelByParam[param.toLowerCase()] : undefined
}

const rangeMinutesByLabel: Record<string, number> = {
  Today: 24 * 60,
  "7 days": 7 * 24 * 60,
  "30 days": 30 * 24 * 60,
}

export function productFiltersFromParams(
  params: URLSearchParams,
  competitorNameForSlug: (slug: string) => string | undefined
): ProductFilters {
  const competitorSlug = params.get("competitor")
  const category = params.get("category")
  return {
    query: params.get("q") ?? "",
    competitor:
      (competitorSlug && competitorNameForSlug(competitorSlug)) ??
      defaultProductFilters.competitor,
    category:
      (category && categoryFromParam(category, filterOptions.categories)) ??
      defaultProductFilters.category,
    changeType: kindFromParam(params.get("change")),
    stock: ["in", "out"].includes(params.get("stock") ?? "")
      ? (params.get("stock") as string)
      : "all",
    dateRange:
      rangeLabelFromParam(params.get("range")) ?? defaultProductFilters.dateRange,
  }
}

export function filterProducts(rows: ProductRow[], f: ProductFilters): ProductRow[] {
  const q = f.query.trim().toLowerCase()
  const maxMinutes = rangeMinutesByLabel[f.dateRange]
  return rows.filter(
    (r) =>
      (!q ||
        r.name.toLowerCase().includes(q) ||
        r.sku.toLowerCase().includes(q) ||
        r.category.toLowerCase().includes(q)) &&
      (f.competitor === defaultProductFilters.competitor ||
        r.competitor === f.competitor) &&
      (f.category === defaultProductFilters.category || r.category === f.category) &&
      (f.changeType === "all" || r.change.kind === f.changeType) &&
      (f.stock === "all" || (f.stock === "in" ? r.inStock : !r.inStock)) &&
      (maxMinutes === undefined || r.lastChangeMinutes <= maxMinutes)
  )
}

export function isValidSort(value: string | null): value is SortValue {
  return (
    !!value &&
    ["recent", "price-low", "price-high", "biggest-drop", "biggest-increase", "newest", "name"].includes(value)
  )
}

export function productsCsv(rows: ProductRow[]): {
  headers: string[]
  rows: (string | number)[][]
} {
  return {
    headers: [
      "Name",
      "SKU",
      "Competitor",
      "Category",
      "Current price",
      "Previous price",
      "Change",
      "In stock",
      "Last change",
      "Source URL",
    ],
    rows: rows.map((r) => [
      r.name,
      r.sku,
      r.competitor,
      r.category,
      r.currentPrice.toFixed(2),
      r.previousPrice === null ? "" : r.previousPrice.toFixed(2),
      r.change.label,
      r.inStock ? "Yes" : "No",
      r.lastChange,
      r.sourceUrl,
    ]),
  }
}
