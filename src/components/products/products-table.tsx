import { useEffect, useMemo, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import {
  Baby,
  Bike,
  Blocks,
  Bone,
  Bot,
  ChevronLeft,
  ChevronRight,
  Download,
  ExternalLink,
  Eye,
  FilterX,
  GitCompareArrows,
  History,
  LineChart,
  MoreHorizontal,
  Package,
  Puzzle,
  Rabbit,
  Search,
  Star,
  TrainFront,
  Waves,
  X,
  type LucideIcon,
} from "lucide-react"
import { toast } from "sonner"

import {
  filterOptions,
  sortOptions,
  type ProductRow,
  type SortValue,
} from "@/lib/products-data"
import {
  defaultProductFilters,
  filterProducts,
  isValidSort,
  productFiltersFromParams,
  productsCsv,
  type ProductFilters,
} from "@/lib/product-filters"
import { categoryParam } from "@/lib/entities"
import { downloadCsv } from "@/lib/csv"
import { paginate } from "@/lib/format"
import { useWorkspace } from "@/lib/workspace-store"
import { cn } from "@/lib/utils"
import { useIsMobile } from "@/hooks/use-mobile"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { EmptyState } from "@/components/shared/empty-state"
import { ChangeBadge } from "@/components/shared/change-badge"
import { ProductIdentity } from "@/components/shared/product-identity"
import { StockBadge } from "@/components/shared/stock-badge"
import { CompareDrawer } from "@/components/products/compare-drawer"

const productIcons: Record<string, LucideIcon> = {
  "lego-castle-set": Blocks,
  "stem-robot-kit": Bot,
  "stem-coding-kit": Bot,
  "wooden-balance-bike": Bike,
  "unicorn-plush-xl": Rabbit,
  "personalised-puzzle": Puzzle,
  "garden-water-table": Waves,
  "baby-sensory-gym": Baby,
  "dinosaur-excavation-kit": Bone,
  "wooden-train-set": TrainFront,
}

const PAGE_SIZE = 8

const priceDelta = (p: ProductRow) =>
  p.previousPrice === null || p.previousPrice === 0
    ? 0
    : (p.currentPrice - p.previousPrice) / p.previousPrice

const sorters: Record<SortValue, (a: ProductRow, b: ProductRow) => number> = {
  recent: (a, b) => a.lastChangeMinutes - b.lastChangeMinutes,
  "price-low": (a, b) => a.currentPrice - b.currentPrice,
  "price-high": (a, b) => b.currentPrice - a.currentPrice,
  "biggest-drop": (a, b) => priceDelta(a) - priceDelta(b),
  "biggest-increase": (a, b) => priceDelta(b) - priceDelta(a),
  newest: (a, b) => b.discoveredAt.localeCompare(a.discoveredAt),
  name: (a, b) => a.name.localeCompare(b.name),
}

const rangeParamByLabel: Record<string, string> = {
  Today: "today",
  "7 days": "7d",
  "30 days": "30d",
}

function RowActions({
  row,
  starred,
  onToggleStar,
  onView,
  onCompare,
  canCompare,
}: {
  row: ProductRow
  starred: boolean
  onToggleStar: () => void
  onView: () => void
  onCompare: () => void
  canCompare: boolean
}) {
  const navigate = useNavigate()
  return (
    <span className="flex items-center justify-end gap-0.5">
      <Button
        variant="ghost"
        size="icon"
        aria-label={starred ? `Remove ${row.name} from watchlist` : `Add ${row.name} to watchlist`}
        onClick={(e) => {
          e.stopPropagation()
          onToggleStar()
        }}
        className={cn(
          "size-7",
          starred ? "text-warning" : "text-muted-foreground/50"
        )}
      >
        <Star className={cn("size-4", starred && "fill-current")} />
      </Button>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            aria-label={`Actions for ${row.name}`}
            className="size-7 text-muted-foreground"
            onClick={(e) => e.stopPropagation()}
          >
            <MoreHorizontal className="size-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
          <DropdownMenuItem onClick={onView}>
            <Eye className="size-3.5" /> View product intelligence
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => navigate(`/products/${row.slug}?tab=price-history`)}
          >
            <LineChart className="size-3.5" /> View price history
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => navigate(`/products/${row.slug}?tab=stock-history`)}
          >
            <History className="size-3.5" /> View stock history
          </DropdownMenuItem>
          <DropdownMenuItem onClick={onCompare} disabled={!canCompare}>
            <GitCompareArrows className="size-3.5" /> Compare competitors
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={() => window.open(row.sourceUrl, "_blank", "noopener,noreferrer")}
          >
            <ExternalLink className="size-3.5" /> Open source page
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </span>
  )
}

export function ProductsTable({
  urlSync = false,
  lockedCompetitor,
  onSelectionChange,
}: {
  /* Mirror filters into ?competitor=&category=&change=&stock=&range=&q=&sort=&page= */
  urlSync?: boolean
  /* Competitor slug: pre-filters rows and hides the competitor select
     (embedded mode on the competitor detail page). */
  lockedCompetitor?: string
  onSelectionChange?: (slugs: string[]) => void
}) {
  const navigate = useNavigate()
  const isMobile = useIsMobile()
  const [searchParams, setSearchParams] = useSearchParams()
  const {
    products,
    watchlist,
    toggleWatchlist,
    addToWatchlist,
    competitorName,
    competitorSlug,
  } = useWorkspace()

  const lockedName = lockedCompetitor ? competitorName(lockedCompetitor) : undefined
  const rows = useMemo(
    () => (lockedName ? products.filter((p) => p.competitor === lockedName) : products),
    [products, lockedName]
  )

  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<ProductFilters>(defaultProductFilters)
  const [sort, setSort] = useState<SortValue>("recent")
  const [page, setPage] = useState(1)
  const [selected, setSelected] = useState<Record<string, boolean>>({})
  const [compareProduct, setCompareProduct] = useState<ProductRow | null>(null)

  useEffect(() => {
    const t = window.setTimeout(() => setLoading(false), 600)
    return () => window.clearTimeout(t)
  }, [])

  /* URL → state, so deep links (KPI cards, activity rows) pre-filter. */
  useEffect(() => {
    if (!urlSync) return
    setFilters(productFiltersFromParams(searchParams, competitorName))
    const sortParam = searchParams.get("sort")
    setSort(isValidSort(sortParam) ? sortParam : "recent")
    const pageParam = Number(searchParams.get("page"))
    setPage(Number.isInteger(pageParam) && pageParam > 0 ? pageParam : 1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlSync, searchParams])

  const writeParams = (
    nextFilters: ProductFilters,
    nextSort: SortValue,
    nextPage: number
  ) => {
    if (!urlSync) return
    const params: Record<string, string> = {}
    if (nextFilters.query.trim()) params.q = nextFilters.query.trim()
    if (nextFilters.competitor !== defaultProductFilters.competitor) {
      params.competitor = competitorSlug(nextFilters.competitor)
    }
    if (nextFilters.category !== defaultProductFilters.category)
      params.category = categoryParam(nextFilters.category)
    if (nextFilters.changeType !== "all") params.change = nextFilters.changeType
    if (nextFilters.stock !== "all") params.stock = nextFilters.stock
    if (nextFilters.dateRange !== defaultProductFilters.dateRange) {
      const token = rangeParamByLabel[nextFilters.dateRange]
      if (token) params.range = token
    }
    if (nextSort !== "recent") params.sort = nextSort
    if (nextPage > 1) params.page = String(nextPage)
    setSearchParams(params, { replace: true })
  }

  const updateFilters = (patch: Partial<ProductFilters>) => {
    const next = { ...filters, ...patch }
    setFilters(next)
    setPage(1)
    writeParams(next, sort, 1)
  }

  const updateSort = (value: SortValue) => {
    setSort(value)
    setPage(1)
    writeParams(filters, value, 1)
  }

  const updatePage = (value: number) => {
    setPage(value)
    writeParams(filters, sort, value)
  }

  const activeFilters =
    (filters.competitor !== defaultProductFilters.competitor && !lockedName ? 1 : 0) +
    (filters.category !== defaultProductFilters.category ? 1 : 0) +
    (filters.changeType !== "all" ? 1 : 0) +
    (filters.stock !== "all" ? 1 : 0) +
    (filters.dateRange !== defaultProductFilters.dateRange ? 1 : 0)

  const clearFilters = () => {
    setFilters(defaultProductFilters)
    setSort("recent")
    setPage(1)
    if (urlSync) setSearchParams({}, { replace: true })
  }

  const visible = useMemo(
    () => [...filterProducts(rows, filters)].sort(sorters[sort]),
    [rows, filters, sort]
  )
  const paged = paginate(visible, page, PAGE_SIZE)

  const selectedSlugs = Object.keys(selected).filter((s) => selected[s])
  const allVisibleSelected =
    paged.slice.length > 0 && paged.slice.every((r) => selected[r.slug])

  useEffect(() => {
    onSelectionChange?.(selectedSlugs)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected])

  const view = (slug: string) => navigate(`/products/${slug}`)

  const bulkCompare = () => {
    if (selectedSlugs.length < 2) {
      toast.info("Select at least two products to compare.")
      return
    }
    const matched = visible.find((r) => selected[r.slug] && r.matched)
    if (matched) setCompareProduct(matched)
    else
      toast.info("No matched listings", {
        description: "The selected products have no matched competitor listings yet.",
      })
  }

  const bulkExport = () => {
    const exportRows = visible.filter((r) => selected[r.slug])
    const csv = productsCsv(exportRows.length > 0 ? exportRows : visible)
    downloadCsv("rivaltracking-products.csv", csv.headers, csv.rows)
    toast.success("Export ready", {
      description: `${csv.rows.length} products exported to CSV.`,
    })
  }

  const bulkWatchlist = async () => {
    const added = await addToWatchlist(selectedSlugs)
    toast.success(
      added > 0
        ? `${added} product${added > 1 ? "s" : ""} added to watchlist`
        : "Already on your watchlist"
    )
  }

  const filterControls = (
    <CardAction className="flex flex-wrap items-center gap-2 max-md:col-span-2 max-md:col-start-1 max-md:row-start-2 max-md:row-span-1 max-md:justify-start md:justify-end">
      <div className="relative">
        <Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search product, SKU, brand or category..."
          value={filters.query}
          onChange={(e) => updateFilters({ query: e.target.value })}
          className="h-8 w-64 pl-8 text-[11px]"
        />
      </div>
      {!lockedName && (
        <Select
          value={filters.competitor}
          onValueChange={(v) => updateFilters({ competitor: v })}
        >
          <SelectTrigger size="sm" className="h-8 text-[10px] font-semibold text-muted-foreground">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {filterOptions.competitors.map((c) => (
              <SelectItem key={c} value={c} className="text-xs">{c}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}
      <Select
        value={filters.category}
        onValueChange={(v) => updateFilters({ category: v })}
      >
        <SelectTrigger size="sm" className="h-8 text-[10px] font-semibold text-muted-foreground">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {filterOptions.categories.map((c) => (
            <SelectItem key={c} value={c} className="text-xs">{c}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select
        value={filters.changeType}
        onValueChange={(v) => updateFilters({ changeType: v })}
      >
        <SelectTrigger size="sm" className="h-8 text-[10px] font-semibold text-muted-foreground">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {filterOptions.changeTypes.map((c) => (
            <SelectItem key={c.value} value={c.value} className="text-xs">
              {c.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select
        value={filters.stock}
        onValueChange={(v) => updateFilters({ stock: v })}
      >
        <SelectTrigger size="sm" className="h-8 text-[10px] font-semibold text-muted-foreground">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {filterOptions.stock.map((s) => (
            <SelectItem key={s.value} value={s.value} className="text-xs">
              {s.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select
        value={filters.dateRange}
        onValueChange={(v) => updateFilters({ dateRange: v })}
      >
        <SelectTrigger size="sm" className="h-8 text-[10px] font-semibold text-muted-foreground">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {filterOptions.dateRanges.map((d) => (
            <SelectItem key={d} value={d} className="text-xs">{d}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      {activeFilters > 0 && (
        <Button
          variant="outline"
          size="sm"
          onClick={clearFilters}
          className="h-8 gap-1.5 text-[10px] font-bold"
        >
          <FilterX className="size-3.5" /> Clear filters
          <Badge className="size-4.5 justify-center rounded-full bg-primary p-0 text-[11px]">
            {activeFilters}
          </Badge>
        </Button>
      )}
      <Select value={sort} onValueChange={(v) => updateSort(v as SortValue)}>
        <SelectTrigger size="sm" className="h-8 text-[10px] font-semibold text-muted-foreground">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {sortOptions.map((s) => (
            <SelectItem key={s.value} value={s.value} className="text-xs">
              {s.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </CardAction>
  )

  const matchedBadge = (row: ProductRow) =>
    row.matched && (
      <Badge
        variant="outline"
        role="button"
        onClick={(e) => {
          e.stopPropagation()
          setCompareProduct(row)
        }}
        className="gap-1 rounded-full border-info/25 bg-info/10 px-2 py-0.5 text-[11px] font-bold text-info hover:bg-info/15"
      >
        <GitCompareArrows className="size-2.5" />
        {row.matched.count} competitors
      </Badge>
    )

  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="gap-3 pb-4">
        <CardTitle className="text-sm font-bold">Product Catalogue</CardTitle>
        {filterControls}
      </CardHeader>

      {selectedSlugs.length > 0 && (
        <div className="mx-4 mb-3 flex flex-wrap items-center gap-2 rounded-xl border border-primary/20 bg-accent px-3.5 py-2">
          <span className="text-[11px] font-bold text-accent-foreground">
            {selectedSlugs.length} product{selectedSlugs.length > 1 ? "s" : ""}{" "}
            selected
          </span>
          <span className="ml-auto flex items-center gap-1.5">
            <Button
              size="sm"
              onClick={bulkCompare}
              className="h-7 rounded-lg px-2.5 text-[10px] font-bold"
            >
              <GitCompareArrows className="size-3" /> Compare
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={bulkExport}
              className="h-7 rounded-lg bg-card px-2.5 text-[10px] font-bold"
            >
              <Download className="size-3" /> Export
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={bulkWatchlist}
              className="h-7 rounded-lg bg-card px-2.5 text-[10px] font-bold"
            >
              <Star className="size-3" /> Add to watchlist
            </Button>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Clear selection"
              onClick={() => setSelected({})}
              className="size-7 text-muted-foreground"
            >
              <X className="size-3.5" />
            </Button>
          </span>
        </div>
      )}

      {loading ? (
        <CardContent className="flex flex-col gap-3 px-4 pb-5">
          {Array.from({ length: 6 }, (_, i) => (
            <div key={i} className="flex items-center gap-3">
              <Skeleton className="size-8.5 rounded-lg" />
              <div className="flex-1 space-y-1.5">
                <Skeleton className="h-3 w-1/3" />
                <Skeleton className="h-2.5 w-1/5" />
              </div>
              <Skeleton className="h-5 w-20 rounded-full" />
              <Skeleton className="h-5 w-16 rounded-full max-md:hidden" />
            </div>
          ))}
        </CardContent>
      ) : rows.length === 0 ? (
        <EmptyState
          icon={Package}
          heading="No products available yet"
          text="Products will appear after the initial competitor scan."
          actionLabel="Add competitor"
          onAction={() => navigate("/competitors")}
        />
      ) : visible.length === 0 ? (
        <EmptyState
          heading="No products found"
          text="Try changing your filters or search query."
        />
      ) : isMobile ? (
        <CardContent className="flex flex-col gap-3 px-4 pb-4">
          {paged.slice.map((row) => (
            <div key={row.slug} className="rounded-xl border p-3.5">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <ProductIdentity
                    icon={productIcons[row.slug] ?? Package}
                    tone={row.tone}
                    name={row.name}
                    sku={row.sku}
                    onClick={() => view(row.slug)}
                  />
                </div>
                <RowActions
                  row={row}
                  starred={watchlist.has(row.slug)}
                  onToggleStar={() => toggleWatchlist(row.slug)}
                  onView={() => view(row.slug)}
                  onCompare={() => setCompareProduct(row)}
                  canCompare={!!row.matched}
                />
              </div>
              <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                <ChangeBadge kind={row.change.kind} label={row.change.label} />
                <StockBadge inStock={row.inStock} />
                {matchedBadge(row)}
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2 text-[10px] text-muted-foreground">
                <div>
                  <span className="block font-medium text-foreground">
                    £{row.currentPrice.toFixed(2)}
                  </span>
                  Current price
                </div>
                <div>
                  <span className="block truncate font-medium text-foreground">
                    {row.competitor}
                  </span>
                  Competitor
                </div>
                <div>
                  <span className="block font-medium text-foreground">
                    {row.lastChange}
                  </span>
                  Last change
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => view(row.slug)}
                className="mt-3 h-8 w-full rounded-lg text-[10px] font-bold"
              >
                View product
              </Button>
            </div>
          ))}
        </CardContent>
      ) : (
        <CardContent className="px-0 pb-0">
          <div className="overflow-x-auto">
            <Table className="min-w-[960px]">
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10 px-3.5">
                    <Checkbox
                      aria-label="Select all visible products"
                      checked={allVisibleSelected}
                      onCheckedChange={(c) => {
                        const next = { ...selected }
                        paged.slice.forEach((r) => (next[r.slug] = !!c))
                        setSelected(next)
                      }}
                    />
                  </TableHead>
                  {[
                    "Product",
                    "Competitor",
                    "Category",
                    "Current Price",
                    "Previous Price",
                    "Change",
                    "Stock",
                    "Last Change",
                    "",
                  ].map((h, i) => (
                    <TableHead key={i} className="px-3.5 text-[10px] font-bold">
                      {h}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {paged.slice.map((row) => (
                  <TableRow
                    key={row.slug}
                    className="text-[11px] text-muted-foreground"
                  >
                    <TableCell className="px-3.5">
                      <Checkbox
                        aria-label={`Select ${row.name}`}
                        checked={!!selected[row.slug]}
                        onCheckedChange={(c) =>
                          setSelected({ ...selected, [row.slug]: !!c })
                        }
                      />
                    </TableCell>
                    <TableCell className="px-3.5 py-2.5">
                      <div className="flex items-center gap-2">
                        <ProductIdentity
                          icon={productIcons[row.slug] ?? Package}
                          tone={row.tone}
                          name={row.name}
                          sku={row.sku}
                          onClick={() => view(row.slug)}
                        />
                        {matchedBadge(row)}
                      </div>
                    </TableCell>
                    <TableCell className="px-3.5">{row.competitor}</TableCell>
                    <TableCell className="px-3.5">{row.category}</TableCell>
                    <TableCell className="px-3.5 font-medium text-foreground">
                      £{row.currentPrice.toFixed(2)}
                    </TableCell>
                    <TableCell className="px-3.5">
                      {row.previousPrice === null
                        ? "—"
                        : `£${row.previousPrice.toFixed(2)}`}
                    </TableCell>
                    <TableCell className="px-3.5">
                      <ChangeBadge
                        kind={row.change.kind}
                        label={row.change.label}
                      />
                    </TableCell>
                    <TableCell className="px-3.5">
                      <StockBadge inStock={row.inStock} />
                    </TableCell>
                    <TableCell className="px-3.5 whitespace-nowrap">
                      {row.lastChange}
                    </TableCell>
                    <TableCell className="px-2 text-right">
                      <RowActions
                        row={row}
                        starred={watchlist.has(row.slug)}
                        onToggleStar={() => toggleWatchlist(row.slug)}
                        onView={() => view(row.slug)}
                        onCompare={() => setCompareProduct(row)}
                        canCompare={!!row.matched}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      )}

      {!loading && visible.length > 0 && (
        <CardFooter className="flex items-center justify-between border-t px-4 py-2.5">
          <span className="text-[10px] text-muted-foreground">
            {paged.from}–{paged.to} of {paged.total.toLocaleString()} products
          </span>
          <span className="flex items-center gap-1">
            <Button
              variant="outline"
              size="icon"
              aria-label="Previous page"
              disabled={paged.page <= 1}
              onClick={() => updatePage(paged.page - 1)}
              className="size-7 rounded-lg"
            >
              <ChevronLeft className="size-3.5" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              aria-label="Next page"
              disabled={paged.page >= paged.pageCount}
              onClick={() => updatePage(paged.page + 1)}
              className="size-7 rounded-lg"
            >
              <ChevronRight className="size-3.5" />
            </Button>
          </span>
        </CardFooter>
      )}

      <CompareDrawer
        product={compareProduct}
        onClose={() => setCompareProduct(null)}
      />
    </Card>
  )
}
