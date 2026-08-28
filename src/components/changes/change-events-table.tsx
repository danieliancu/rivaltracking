import { useEffect, useMemo, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"

import {
  Bell,
  ChevronLeft,
  ChevronRight,
  Download,
  ExternalLink,
  Eye,
  FilterX,
  History,
  MoreHorizontal,
  Search,
  Sparkles,
  Star,
  X,
} from "lucide-react"
import { toast } from "sonner"

import {
  changeFilterOptions,
  changeSortOptions,
  savedViews,
  type ChangeEvent,
  type ChangePattern,
  type ChangeSortValue,
} from "@/lib/changes-data"
import {
  changeFiltersFromParams,
  changeRangeParamByLabel,
  changesCsv,
  defaultChangeFilters,
  filterChanges,
  type ChangeFilters,
} from "@/lib/change-filters"
import { categoryParam } from "@/lib/entities"
import { downloadCsv } from "@/lib/csv"
import { paginate } from "@/lib/format"
import { useWorkspace } from "@/lib/workspace-store"
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
  SelectGroup,
  SelectItem,
  SelectLabel,
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
import { ChangeBadge } from "@/components/shared/change-badge"
import { ChangeValue } from "@/components/shared/change-value"
import { EmptyState } from "@/components/shared/empty-state"
import { ImpactBadge } from "@/components/shared/impact-badge"
import { ProductIdentity } from "@/components/shared/product-identity"

const PAGE_SIZE = 8

const impactRank = { high: 0, medium: 1, low: 2 } as const

const pct = (e: ChangeEvent) =>
  e.secondary ? parseFloat(e.secondary.replace("%", "")) : 0

const sorters: Record<
  ChangeSortValue,
  (a: ChangeEvent, b: ChangeEvent) => number
> = {
  recent: (a, b) => a.detectedMinutes - b.detectedMinutes,
  impact: (a, b) => impactRank[a.impact] - impactRank[b.impact],
  "biggest-drop": (a, b) => pct(a) - pct(b),
  "biggest-increase": (a, b) => pct(b) - pct(a),
  competitor: (a, b) => a.competitor.localeCompare(b.competitor),
  product: (a, b) => a.product.name.localeCompare(b.product.name),
}

function isValidChangeSort(value: string | null): value is ChangeSortValue {
  return (
    !!value && changeSortOptions.some((s) => s.value === value)
  )
}

function RowActions({
  event,
  onDetails,
}: {
  event: ChangeEvent
  onDetails: () => void
}) {
  const navigate = useNavigate()
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Actions for ${event.product.name}`}
          className="size-7 text-muted-foreground"
          onClick={(e) => e.stopPropagation()}
        >
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
        <DropdownMenuItem onClick={onDetails}>
          <Eye className="size-3.5" /> View details
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => navigate(`/products/${event.product.slug}`)}
        >
          <History className="size-3.5" /> View product history
        </DropdownMenuItem>
        <DropdownMenuItem
          disabled={!event.sourceUrl}
          onClick={() =>
            event.sourceUrl &&
            window.open(event.sourceUrl, "_blank", "noopener,noreferrer")
          }
        >
          <ExternalLink className="size-3.5" /> View source product
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={() =>
            navigate("/alerts", {
              state: {
                createAlert: {
                  competitor: event.competitor,
                  kind: event.kind,
                  category: event.category,
                },
              },
            })
          }
        >
          <Bell className="size-3.5" /> Create alert
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export function ChangeEventsTable({
  pattern,
  onOpenDetails,
  urlSync = false,
}: {
  pattern: ChangePattern | null
  onOpenDetails: (event: ChangeEvent) => void
  /* Mirror filters into ?competitor=&type=&category=&impact=&range=&product=&q=&sort=&page= */
  urlSync?: boolean
}) {
  const navigate = useNavigate()
  const isMobile = useIsMobile()
  const [searchParams, setSearchParams] = useSearchParams()
  const {
    changeEvents: rows,
    addToWatchlist,
    competitorName,
    competitorSlug,
  } = useWorkspace()

  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<ChangeFilters>(defaultChangeFilters)
  const [sort, setSort] = useState<ChangeSortValue>("recent")
  const [page, setPage] = useState(1)
  const [view, setView] = useState("none")
  const [selected, setSelected] = useState<Record<number, boolean>>({})

  useEffect(() => {
    const t = window.setTimeout(() => setLoading(false), 600)
    return () => window.clearTimeout(t)
  }, [])

  /* URL → state, so deep links (KPI cards, activity rows, product pages)
     pre-filter the table. */
  useEffect(() => {
    if (!urlSync) return
    setFilters(changeFiltersFromParams(searchParams, competitorName))
    const sortParam = searchParams.get("sort")
    setSort(isValidChangeSort(sortParam) ? sortParam : "recent")
    const pageParam = Number(searchParams.get("page"))
    setPage(Number.isInteger(pageParam) && pageParam > 0 ? pageParam : 1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlSync, searchParams])

  const writeParams = (
    nextFilters: ChangeFilters,
    nextSort: ChangeSortValue,
    nextPage: number,
    patternId?: string
  ) => {
    if (!urlSync) return
    const params: Record<string, string> = {}
    if (nextFilters.query.trim()) params.q = nextFilters.query.trim()
    if (nextFilters.competitor !== defaultChangeFilters.competitor) {
      params.competitor = competitorSlug(nextFilters.competitor)
    }
    if (nextFilters.changeType !== "all") params.type = nextFilters.changeType
    if (nextFilters.category !== defaultChangeFilters.category)
      params.category = categoryParam(nextFilters.category)
    if (nextFilters.importance !== "all") params.impact = nextFilters.importance
    if (nextFilters.dateRange !== defaultChangeFilters.dateRange) {
      const token = changeRangeParamByLabel[nextFilters.dateRange]
      if (token) params.range = token
    }
    if (nextFilters.productSlug) params.product = nextFilters.productSlug
    if (nextSort !== "recent") params.sort = nextSort
    if (nextPage > 1) params.page = String(nextPage)
    if (patternId) params.pattern = patternId
    setSearchParams(params, { replace: true })
  }

  const updateFilters = (patch: Partial<ChangeFilters>) => {
    const next = { ...filters, ...patch }
    setFilters(next)
    setPage(1)
    writeParams(next, sort, 1)
  }

  const updateSort = (value: ChangeSortValue) => {
    setSort(value)
    setPage(1)
    writeParams(filters, value, 1)
  }

  const updatePage = (value: number) => {
    setPage(value)
    writeParams(filters, sort, value)
  }

  /* A pattern card CTA applies that pattern's backend-provided filters. */
  useEffect(() => {
    if (!pattern) return
    const next: ChangeFilters = {
      ...defaultChangeFilters,
      dateRange: "30 days",
      competitor: pattern.filters.competitor ?? defaultChangeFilters.competitor,
      changeType: pattern.filters.kind ?? "all",
      category: pattern.filters.category ?? defaultChangeFilters.category,
    }
    setFilters(next)
    setView("none")
    setPage(1)
    writeParams(next, sort, 1, pattern.id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pattern])

  const applyView = (id: string) => {
    setView(id)
    const v = savedViews.find((s) => s.id === id)
    if (!v) return
    updateFilters({
      competitor: v.filters.competitor ?? defaultChangeFilters.competitor,
      changeType: v.filters.kind ?? "all",
      importance: v.filters.importance ?? "all",
    })
  }

  const activeFilters =
    (filters.competitor !== defaultChangeFilters.competitor ? 1 : 0) +
    (filters.changeType !== "all" ? 1 : 0) +
    (filters.category !== defaultChangeFilters.category ? 1 : 0) +
    (filters.importance !== "all" ? 1 : 0) +
    (filters.dateRange !== defaultChangeFilters.dateRange ? 1 : 0) +
    (filters.productSlug ? 1 : 0)

  const clearFilters = () => {
    setFilters(defaultChangeFilters)
    setSort("recent")
    setView("none")
    setPage(1)
    if (urlSync) setSearchParams({}, { replace: true })
  }

  const visible = useMemo(
    () => [...filterChanges(rows, filters)].sort(sorters[sort]),
    [rows, filters, sort]
  )
  const paged = paginate(visible, page, PAGE_SIZE)

  const selectedIds = Object.keys(selected).filter((k) => selected[Number(k)])
  const allVisibleSelected =
    paged.slice.length > 0 && paged.slice.every((r) => selected[r.id])

  const selectedEvents = visible.filter((r) => selected[r.id])

  const bulkExport = () => {
    const csv = changesCsv(selectedEvents.length > 0 ? selectedEvents : visible)
    downloadCsv("rivaltracking-changes.csv", csv.headers, csv.rows)
    toast.success("Export ready", {
      description: `${csv.rows.length} changes exported to CSV.`,
    })
  }

  const bulkAskAI = () => {
    navigate("/ask-ai", {
      state: {
        prompt: `Explain these ${selectedEvents.length} selected changes and what they mean for my pricing strategy`,
      },
    })
  }

  const bulkWatchlist = async () => {
    const slugs = [...new Set(selectedEvents.map((e) => e.product.slug))]
    const added = await addToWatchlist(slugs)
    toast.success(
      added > 0
        ? `${added} product${added > 1 ? "s" : ""} added to watchlist`
        : "Already on your watchlist"
    )
  }

  const selectSize = "h-8 text-[10px] font-semibold text-muted-foreground"

  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="gap-3 pb-4">
        <CardTitle className="text-sm font-bold">Change Events</CardTitle>
        <CardAction className="flex flex-wrap items-center gap-2 max-md:col-span-2 max-md:col-start-1 max-md:row-start-2 max-md:row-span-1 max-md:justify-start md:justify-end">
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search product, competitor or category..."
              value={filters.query}
              onChange={(e) => updateFilters({ query: e.target.value })}
              className="h-8 w-64 pl-8 text-[11px]"
            />
          </div>
          <Select
            value={filters.competitor}
            onValueChange={(v) => updateFilters({ competitor: v })}
          >
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {changeFilterOptions.competitors.map((c) => (
                <SelectItem key={c} value={c} className="text-xs">{c}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={filters.changeType}
            onValueChange={(v) => updateFilters({ changeType: v })}
          >
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all" className="text-xs">All changes</SelectItem>
              {changeFilterOptions.changeTypeGroups.map((g) => (
                <SelectGroup key={g.label}>
                  <SelectLabel className="text-[10px] text-muted-foreground">
                    {g.label}
                  </SelectLabel>
                  {g.options.map((o) => (
                    <SelectItem key={o.value} value={o.value} className="text-xs">
                      {o.label}
                    </SelectItem>
                  ))}
                </SelectGroup>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={filters.category}
            onValueChange={(v) => updateFilters({ category: v })}
          >
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {changeFilterOptions.categories.map((c) => (
                <SelectItem key={c} value={c} className="text-xs">{c}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={filters.importance}
            onValueChange={(v) => updateFilters({ importance: v })}
          >
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {changeFilterOptions.importance.map((i) => (
                <SelectItem key={i.value} value={i.value} className="text-xs">
                  {i.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={filters.dateRange}
            onValueChange={(v) => updateFilters({ dateRange: v })}
          >
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {changeFilterOptions.dateRanges.map((d) => (
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
          <Select
            value={sort}
            onValueChange={(v) => updateSort(v as ChangeSortValue)}
          >
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {changeSortOptions.map((s) => (
                <SelectItem key={s.value} value={s.value} className="text-xs">
                  {s.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={view} onValueChange={applyView}>
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue placeholder="My Views" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none" className="text-xs">My Views</SelectItem>
              {savedViews.map((v) => (
                <SelectItem key={v.id} value={v.id} className="text-xs">
                  {v.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="ghost"
            size="sm"
            onClick={() =>
              navigate("/alerts", {
                state: {
                  createAlert: {
                    competitor: filters.competitor,
                    kind: filters.changeType,
                    category: filters.category,
                  },
                },
              })
            }
            className="h-8 gap-1.5 text-[10px] font-bold text-muted-foreground"
          >
            <Bell className="size-3.5" /> Create alert from filters
          </Button>
        </CardAction>
      </CardHeader>

      {selectedIds.length > 0 && (
        <div className="mx-4 mb-3 flex flex-wrap items-center gap-2 rounded-xl border border-primary/20 bg-accent px-3.5 py-2">
          <span className="text-[11px] font-bold text-accent-foreground">
            {selectedIds.length} change{selectedIds.length > 1 ? "s" : ""}{" "}
            selected
          </span>
          <span className="ml-auto flex items-center gap-1.5">
            <Button
              variant="outline"
              size="sm"
              onClick={bulkExport}
              className="h-7 rounded-lg bg-card px-2.5 text-[10px] font-bold"
            >
              <Download className="size-3" /> Export
            </Button>
            <Button
              size="sm"
              onClick={bulkAskAI}
              className="h-7 rounded-lg px-2.5 text-[10px] font-bold"
            >
              <Sparkles className="size-3" /> Ask AI
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={bulkWatchlist}
              className="h-7 rounded-lg bg-card px-2.5 text-[10px] font-bold"
            >
              <Star className="size-3" /> Add products to watchlist
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
              <Skeleton className="h-5 w-24 rounded-full" />
              <Skeleton className="size-8.5 rounded-lg" />
              <div className="flex-1 space-y-1.5">
                <Skeleton className="h-3 w-1/3" />
                <Skeleton className="h-2.5 w-1/5" />
              </div>
              <Skeleton className="h-5 w-28 max-md:hidden" />
              <Skeleton className="h-5 w-14 rounded-full max-md:hidden" />
            </div>
          ))}
        </CardContent>
      ) : rows.length === 0 ? (
        <EmptyState
          heading="Monitoring has started"
          text="Change history will begin after the next successful scan."
        />
      ) : visible.length === 0 ? (
        <EmptyState
          heading="No changes found"
          text="Try adjusting your filters or selecting a wider date range."
        />
      ) : isMobile ? (
        <CardContent className="flex flex-col gap-3 px-4 pb-4">
          {paged.slice.map((row) => (
            <div
              key={row.id}
              onClick={() => onOpenDetails(row)}
              className="cursor-pointer rounded-xl border p-3.5"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <ProductIdentity
                    icon={row.product.icon}
                    tone={row.product.tone}
                    name={row.product.name}
                    sku={row.competitor}
                  />
                </div>
                <RowActions event={row} onDetails={() => onOpenDetails(row)} />
              </div>
              <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                <ChangeBadge kind={row.kind} label={row.label} />
                <ImpactBadge impact={row.impact} />
              </div>
              <div className="mt-3 flex items-center justify-between gap-2 text-[11px] text-muted-foreground">
                <ChangeValue
                  previous={row.previous}
                  current={row.current}
                  secondary={row.secondary}
                  secondaryTone={row.secondaryTone ?? "muted"}
                />
                <span>{row.detected}</span>
              </div>
            </div>
          ))}
        </CardContent>
      ) : (
        <CardContent className="px-0 pb-0">
          <div className="overflow-x-auto">
            <Table className="min-w-[1020px]">
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10 px-3.5">
                    <Checkbox
                      aria-label="Select all visible changes"
                      checked={allVisibleSelected}
                      onCheckedChange={(c) => {
                        const next = { ...selected }
                        paged.slice.forEach((r) => (next[r.id] = !!c))
                        setSelected(next)
                      }}
                    />
                  </TableHead>
                  {[
                    "Change",
                    "Product",
                    "Competitor",
                    "Previous",
                    "Current",
                    "Category",
                    "Impact",
                    "Detected",
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
                    key={row.id}
                    onClick={() => onOpenDetails(row)}
                    className="cursor-pointer text-[11px] text-muted-foreground"
                  >
                    <TableCell
                      className="px-3.5"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Checkbox
                        aria-label={`Select change for ${row.product.name}`}
                        checked={!!selected[row.id]}
                        onCheckedChange={(c) =>
                          setSelected({ ...selected, [row.id]: !!c })
                        }
                      />
                    </TableCell>
                    <TableCell className="px-3.5">
                      <ChangeBadge kind={row.kind} label={row.label} />
                    </TableCell>
                    <TableCell className="px-3.5 py-2.5">
                      <ProductIdentity
                        icon={row.product.icon}
                        tone={row.product.tone}
                        name={row.product.name}
                        sku={row.product.sku}
                      />
                    </TableCell>
                    <TableCell className="px-3.5">{row.competitor}</TableCell>
                    <TableCell className="max-w-44 truncate px-3.5">
                      {row.previous}
                    </TableCell>
                    <TableCell className="px-3.5">
                      <span className="flex max-w-52 flex-col gap-0.5">
                        <span className="truncate font-medium text-foreground">
                          {row.current}
                        </span>
                        {row.secondary && (
                          <span
                            className={
                              row.secondaryTone === "success"
                                ? "text-[11px] font-medium text-success"
                                : row.secondaryTone === "destructive"
                                  ? "text-[11px] font-medium text-destructive"
                                  : "text-[11px] font-medium text-muted-foreground"
                            }
                          >
                            {row.secondary}
                          </span>
                        )}
                      </span>
                    </TableCell>
                    <TableCell className="px-3.5">{row.category}</TableCell>
                    <TableCell className="px-3.5">
                      <ImpactBadge impact={row.impact} />
                    </TableCell>
                    <TableCell className="px-3.5 whitespace-nowrap">
                      {row.detected}
                    </TableCell>
                    <TableCell className="px-2 text-right">
                      <RowActions
                        event={row}
                        onDetails={() => onOpenDetails(row)}
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
            {paged.from}–{paged.to} of {paged.total.toLocaleString()} changes
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
    </Card>
  )
}
