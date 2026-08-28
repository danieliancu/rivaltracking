import { useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import {
  ArrowDown,
  ArrowUp,
  Loader2,
  MoreHorizontal,
  Pause,
  Play,
  Search,
  Settings2,
  Trash2,
  Eye,
} from "lucide-react"

import { type CompetitorRow } from "@/lib/competitors-data"
import { cn } from "@/lib/utils"
import { useIsMobile } from "@/hooks/use-mobile"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { CompetitorIdentity } from "@/components/shared/competitor-identity"
import { StatusBadge } from "@/components/shared/status-badge"

type Filter = "all" | "healthy" | "attention" | "scanning"
type Sort = "activity" | "recent" | "products" | "scanned"

const sortLabels: Record<Sort, string> = {
  activity: "Most activity",
  recent: "Recently added",
  products: "Most products",
  scanned: "Last scanned",
}

function num(v: number | null) {
  return v === null ? "—" : v.toLocaleString()
}

function RowActions({
  row,
  onRemove,
  onViewCompetitor,
  onRunScan,
  onPauseResume,
  onSettings,
}: {
  row: CompetitorRow
  onRemove: () => void
  onViewCompetitor: () => void
  onRunScan: () => void
  onPauseResume: () => void
  onSettings: () => void
}) {
  const paused = row.status === "paused"
  return (
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
        <DropdownMenuItem onClick={onViewCompetitor}>
          <Eye className="size-3.5" /> View competitor
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onRunScan} disabled={paused}>
          <Play className="size-3.5" /> Run scan
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onPauseResume}>
          {paused ? (
            <>
              <Play className="size-3.5" /> Resume monitoring
            </>
          ) : (
            <>
              <Pause className="size-3.5" /> Pause monitoring
            </>
          )}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onSettings}>
          <Settings2 className="size-3.5" /> Monitoring settings
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem variant="destructive" onClick={onRemove}>
          <Trash2 className="size-3.5" /> Remove competitor
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

function LastScanCell({ row }: { row: CompetitorRow }) {
  if (row.status === "scanning") {
    return (
      <span className="flex items-center gap-1.5 font-semibold text-info">
        <Loader2 className="size-3 animate-spin" /> Scanning now
      </span>
    )
  }
  return <>{row.lastScan}</>
}

export function CompetitorsTable({
  rows,
  onRemoveRow,
  onRunScan,
  onPauseResume,
  onSettings,
}: {
  rows: CompetitorRow[]
  onRemoveRow: (slug: string) => void
  onRunScan: (row: CompetitorRow) => void
  onPauseResume: (row: CompetitorRow) => void
  onSettings: (row: CompetitorRow) => void
}) {
  const navigate = useNavigate()
  const isMobile = useIsMobile()
  const [query, setQuery] = useState("")
  const [filter, setFilter] = useState<Filter>("all")
  const [sort, setSort] = useState<Sort>("activity")
  const [toRemove, setToRemove] = useState<CompetitorRow | null>(null)

  const visible = useMemo(() => {
    let out = rows.filter((r) =>
      r.name.toLowerCase().includes(query.trim().toLowerCase())
    )
    if (filter !== "all") out = out.filter((r) => r.status === filter)
    const bySort: Record<Sort, (a: CompetitorRow, b: CompetitorRow) => number> = {
      activity: (a, b) => (b.changesToday ?? -1) - (a.changesToday ?? -1),
      recent: (a, b) => b.addedAt.localeCompare(a.addedAt),
      products: (a, b) => (b.products ?? -1) - (a.products ?? -1),
      scanned: (a, b) =>
        (a.lastScanMinutes ?? Number.MAX_SAFE_INTEGER) -
        (b.lastScanMinutes ?? Number.MAX_SAFE_INTEGER),
    }
    return [...out].sort(bySort[sort])
  }, [rows, query, filter, sort])

  const view = (slug: string) => navigate(`/competitors/${slug}`)

  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="gap-3 pb-4">
        <CardTitle className="text-sm font-bold">Monitored Competitors</CardTitle>
        <CardAction className="flex flex-wrap items-center gap-2 max-md:col-span-2 max-md:col-start-1 max-md:row-start-2 max-md:row-span-1 max-md:justify-start md:justify-end">
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search competitors..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="h-8 w-44 pl-8 text-[11px]"
            />
          </div>
          <Tabs value={filter} onValueChange={(v) => setFilter(v as Filter)}>
            <TabsList className="h-8 rounded-lg">
              {(["all", "healthy", "attention", "scanning"] as const).map((f) => (
                <TabsTrigger
                  key={f}
                  value={f}
                  className="rounded-md px-2.5 text-[10px] font-semibold capitalize data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
                >
                  {f}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
          <Select value={sort} onValueChange={(v) => setSort(v as Sort)}>
            <SelectTrigger
              size="sm"
              className="h-8 w-36 text-[10px] font-semibold text-muted-foreground"
            >
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {(Object.keys(sortLabels) as Sort[]).map((s) => (
                <SelectItem key={s} value={s} className="text-xs">
                  {sortLabels[s]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>

      {isMobile ? (
        <CardContent className="flex flex-col gap-3 px-4 pb-4">
          {visible.map((row) => (
            <div key={row.slug} className="rounded-xl border p-3.5">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <CompetitorIdentity name={row.name} url={row.url} />
                </div>
                <div className="flex shrink-0 items-center gap-1">
                  <StatusBadge status={row.status} />
                  <RowActions
                    row={row}
                    onRemove={() => setToRemove(row)}
                    onViewCompetitor={() => view(row.slug)}
                    onRunScan={() => onRunScan(row)}
                    onPauseResume={() => onPauseResume(row)}
                    onSettings={() => onSettings(row)}
                  />
                </div>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2 text-[10px] text-muted-foreground">
                <div>
                  <span className="block font-medium text-foreground">
                    {num(row.products)}
                  </span>
                  Products
                </div>
                <div>
                  <span className="block font-medium text-foreground">
                    {row.changesToday === null ? "—" : `${row.changesToday} today`}
                  </span>
                  Changes
                </div>
                <div>
                  <span className="block font-medium text-foreground">
                    <LastScanCell row={row} />
                  </span>
                  Last scan
                </div>
              </div>
              {row.note && (
                <p className="mt-2 text-[10px] text-muted-foreground">{row.note}</p>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={() => view(row.slug)}
                className="mt-3 h-8 w-full rounded-lg text-[10px] font-bold"
              >
                View competitor
              </Button>
            </div>
          ))}
        </CardContent>
      ) : (
        <CardContent className="px-0 pb-0">
          <div className="overflow-x-auto">
            <Table className="min-w-[860px]">
              <TableHeader>
                <TableRow>
                  {[
                    "Competitor",
                    "Market",
                    "Products",
                    "Changes",
                    "Price Changes",
                    "Stock Changes",
                    "Last Scan",
                    "Status",
                    "",
                  ].map((h, i) => (
                    <TableHead key={i} className="px-3.5 text-[10px] font-bold">
                      {h}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {visible.map((row) => (
                  <TableRow
                    key={row.slug}
                    onClick={() => view(row.slug)}
                    className="cursor-pointer text-[11px] text-muted-foreground"
                  >
                    <TableCell className="px-3.5 py-2.5">
                      <CompetitorIdentity name={row.name} url={row.url} />
                    </TableCell>
                    <TableCell className="px-3.5">
                      <Badge
                        variant="secondary"
                        className="rounded-full text-[11px] font-bold text-muted-foreground"
                      >
                        {row.market}
                      </Badge>
                    </TableCell>
                    <TableCell className="px-3.5 font-medium text-foreground">
                      {num(row.products)}
                    </TableCell>
                    <TableCell className="px-3.5">
                      {row.changesToday === null ? (
                        "—"
                      ) : (
                        <>
                          <span className="font-medium text-foreground">
                            {row.changesToday}
                          </span>{" "}
                          today
                        </>
                      )}
                    </TableCell>
                    <TableCell className="px-3.5">
                      {row.priceDrops === null ? (
                        "—"
                      ) : (
                        <span className="flex items-center gap-1 font-medium">
                          <span className="flex items-center text-success">
                            {row.priceDrops} <ArrowDown className="size-3" />
                          </span>
                          <span className="text-muted-foreground/60">/</span>
                          <span className="flex items-center text-destructive">
                            {row.priceIncreases} <ArrowUp className="size-3" />
                          </span>
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="px-3.5">{num(row.stockChanges)}</TableCell>
                    <TableCell className="px-3.5">
                      <LastScanCell row={row} />
                    </TableCell>
                    <TableCell className="px-3.5">
                      {row.note && row.status === "attention" ? (
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <span className="inline-flex">
                              <StatusBadge status={row.status} />
                            </span>
                          </TooltipTrigger>
                          <TooltipContent className="text-[11px]">
                            {row.note}
                          </TooltipContent>
                        </Tooltip>
                      ) : (
                        <span>
                          <StatusBadge status={row.status} />
                          {row.note && (
                            <span className="mt-1 block text-[11px]">{row.note}</span>
                          )}
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="px-2 text-right">
                      <RowActions
                        row={row}
                        onRemove={() => setToRemove(row)}
                        onViewCompetitor={() => view(row.slug)}
                        onRunScan={() => onRunScan(row)}
                        onPauseResume={() => onPauseResume(row)}
                        onSettings={() => onSettings(row)}
                      />
                    </TableCell>
                  </TableRow>
                ))}
                {visible.length === 0 && (
                  <TableRow>
                    <TableCell
                      colSpan={9}
                      className={cn(
                        "px-3.5 py-8 text-center text-xs text-muted-foreground"
                      )}
                    >
                      No competitors match your search.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      )}

      <AlertDialog open={!!toRemove} onOpenChange={(o) => !o && setToRemove(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-base">
              Remove {toRemove?.name}?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-xs">
              Monitoring will stop and the collected snapshots for this
              competitor will no longer be updated. This action cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="h-9 text-xs font-semibold">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (toRemove) onRemoveRow(toRemove.slug)
                setToRemove(null)
              }}
              className="h-9 bg-destructive text-xs font-bold text-destructive-foreground hover:bg-destructive/90"
            >
              Remove competitor
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  )
}
