import { useMemo, useState } from "react"
import {
  Bell,
  Copy,
  History,
  MoreHorizontal,
  Pause,
  Pencil,
  Play,
  Search,
  Trash2,
} from "lucide-react"

import {
  alertFilterOptions,
  typeGroupMeta,
  type AlertRule,
} from "@/lib/alerts-data"
import { useWorkspace } from "@/lib/workspace-store"
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
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
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
import { EmptyState } from "@/components/shared/empty-state"
import { ImpactBadge } from "@/components/shared/impact-badge"
import { AlertRuleStatusBadge } from "@/components/alerts/alert-status-badge"

const priorityRank = { high: 0, medium: 1, low: 2 } as const

function RuleName({ rule }: { rule: AlertRule }) {
  const meta = typeGroupMeta[rule.typeGroup]
  const Icon = meta.icon
  return (
    <div className="flex items-center gap-2.5">
      <span
        className={cn(
          "flex size-8.5 shrink-0 items-center justify-center rounded-lg",
          meta.tone
        )}
      >
        <Icon className="size-4" />
      </span>
      <span className="min-w-0">
        <span className="flex items-center gap-1.5">
          <span className="truncate text-sm font-medium text-foreground">
            {rule.name}
          </span>
          {rule.priority && <ImpactBadge impact={rule.priority} />}
        </span>
        <span className="mt-0.5 block text-[11px] text-muted-foreground">
          {meta.label}
          {rule.patternBased && " · Based on detected change patterns"}
        </span>
      </span>
    </div>
  )
}

function RuleActions({
  rule,
  onToggle,
  onDelete,
  onEdit,
  onDuplicate,
  onHistory,
}: {
  rule: AlertRule
  onToggle: () => void
  onDelete: () => void
  onEdit: () => void
  onDuplicate: () => void
  onHistory: () => void
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Actions for ${rule.name}`}
          className="size-7 text-muted-foreground"
          onClick={(e) => e.stopPropagation()}
        >
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
        <DropdownMenuItem onClick={onEdit}>
          <Pencil className="size-3.5" /> Edit
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onToggle}>
          {rule.active ? (
            <>
              <Pause className="size-3.5" /> Pause
            </>
          ) : (
            <>
              <Play className="size-3.5" /> Resume
            </>
          )}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onDuplicate}>
          <Copy className="size-3.5" /> Duplicate
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onHistory}>
          <History className="size-3.5" /> View history
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem variant="destructive" onClick={onDelete}>
          <Trash2 className="size-3.5" /> Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export function AlertRulesTable({
  rules,
  onToggleRule,
  onDeleteRule,
  onCreate,
  onEditRule,
  onDuplicateRule,
  onViewHistory,
}: {
  rules: AlertRule[]
  onToggleRule: (id: string) => void
  onDeleteRule: (id: string) => void
  onCreate: () => void
  onEditRule: (rule: AlertRule) => void
  onDuplicateRule: (rule: AlertRule) => void
  onViewHistory: (rule: AlertRule) => void
}) {
  const isMobile = useIsMobile()
  const { competitors } = useWorkspace()
  const [query, setQuery] = useState("")
  const [status, setStatus] = useState("all")
  const [type, setType] = useState("all")
  const [competitor, setCompetitor] = useState("All competitors")
  const [sort, setSort] = useState("triggered")
  const [toDelete, setToDelete] = useState<AlertRule | null>(null)

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase()
    const out = rules.filter(
      (r) =>
        (!q || r.name.toLowerCase().includes(q) || r.condition.toLowerCase().includes(q)) &&
        (status === "all" || (status === "active" ? r.active : !r.active)) &&
        (type === "all" || r.typeGroup === type) &&
        (competitor === "All competitors" || r.competitors === competitor)
    )
    const sorters: Record<string, (a: AlertRule, b: AlertRule) => number> = {
      triggered: (a, b) =>
        (a.lastTriggeredMinutes ?? Number.MAX_SAFE_INTEGER) -
        (b.lastTriggeredMinutes ?? Number.MAX_SAFE_INTEGER),
      created: (a, b) => b.createdAt.localeCompare(a.createdAt),
      priority: (a, b) =>
        priorityRank[a.priority ?? "low"] - priorityRank[b.priority ?? "low"],
      name: (a, b) => a.name.localeCompare(b.name),
    }
    return [...out].sort(sorters[sort])
  }, [rules, query, status, type, competitor, sort])

  const selectSize = "h-8 text-[10px] font-semibold text-muted-foreground"

  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="gap-3 pb-4">
        <CardTitle className="text-sm font-bold">Alert Rules</CardTitle>
        <CardDescription className="text-xs">
          Your monitoring rules for competitor activity.
        </CardDescription>
        <CardAction className="flex flex-wrap items-center gap-2 max-md:col-span-2 max-md:col-start-1 max-md:row-start-3 max-md:row-span-1 max-md:justify-start md:justify-end">
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search alerts..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="h-8 w-44 pl-8 text-[11px]"
            />
          </div>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {alertFilterOptions.statuses.map((s) => (
                <SelectItem key={s.value} value={s.value} className="text-xs">
                  {s.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={type} onValueChange={setType}>
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {alertFilterOptions.types.map((t) => (
                <SelectItem key={t.value} value={t.value} className="text-xs">
                  {t.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={competitor} onValueChange={setCompetitor}>
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {["All competitors", ...competitors.map((c) => c.name)].map((c) => (
                <SelectItem key={c} value={c} className="text-xs">
                  {c}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={sort} onValueChange={setSort}>
            <SelectTrigger size="sm" className={selectSize}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {alertFilterOptions.sorts.map((s) => (
                <SelectItem key={s.value} value={s.value} className="text-xs">
                  {s.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>

      {rules.length === 0 ? (
        <EmptyState
          icon={Bell}
          heading="Never miss an important competitor move"
          text="Create alerts for price changes, stock activity, new products and promotions."
          actionLabel="Create your first alert"
          onAction={onCreate}
        />
      ) : visible.length === 0 ? (
        <EmptyState
          heading="No alert rules found"
          text="Try adjusting your search or filters."
        />
      ) : isMobile ? (
        <CardContent className="flex flex-col gap-3 px-4 pb-4">
          {visible.map((rule) => (
            <div key={rule.id} className="rounded-xl border p-3.5">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <RuleName rule={rule} />
                </div>
                <RuleActions
                  rule={rule}
                  onToggle={() => onToggleRule(rule.id)}
                  onDelete={() => setToDelete(rule)}
                  onEdit={() => onEditRule(rule)}
                  onDuplicate={() => onDuplicateRule(rule)}
                  onHistory={() => onViewHistory(rule)}
                />
              </div>
              <p className="mt-2.5 text-[11px] text-muted-foreground">
                {rule.condition}
              </p>
              <div className="mt-2 flex flex-wrap items-center gap-1.5">
                <AlertRuleStatusBadge active={rule.active} />
                <span className="text-[11px] text-muted-foreground">
                  {rule.competitors}
                  {rule.category && ` · ${rule.category}`} · {rule.frequency} ·
                  Last triggered {rule.lastTriggered}
                </span>
              </div>
            </div>
          ))}
        </CardContent>
      ) : (
        <CardContent className="px-0 pb-0">
          <div className="overflow-x-auto">
            <Table className="min-w-[980px]">
              <TableHeader>
                <TableRow>
                  {[
                    "Alert",
                    "Condition",
                    "Competitors",
                    "Frequency",
                    "Last Triggered",
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
                {visible.map((rule) => (
                  <TableRow key={rule.id} className="text-[11px] text-muted-foreground">
                    <TableCell className="px-3.5 py-2.5">
                      <RuleName rule={rule} />
                    </TableCell>
                    <TableCell className="max-w-56 px-3.5">
                      {rule.condition}
                    </TableCell>
                    <TableCell className="px-3.5">
                      <span>
                        <span className="block">{rule.competitors}</span>
                        {rule.category && (
                          <span className="mt-0.5 block text-[11px] text-muted-foreground/70">
                            {rule.category}
                          </span>
                        )}
                      </span>
                    </TableCell>
                    <TableCell className="px-3.5">{rule.frequency}</TableCell>
                    <TableCell className="px-3.5 whitespace-nowrap">
                      {rule.lastTriggered}
                    </TableCell>
                    <TableCell className="px-3.5">
                      <AlertRuleStatusBadge active={rule.active} />
                    </TableCell>
                    <TableCell className="px-2 text-right">
                      <RuleActions
                        rule={rule}
                        onToggle={() => onToggleRule(rule.id)}
                        onDelete={() => setToDelete(rule)}
                        onEdit={() => onEditRule(rule)}
                        onDuplicate={() => onDuplicateRule(rule)}
                        onHistory={() => onViewHistory(rule)}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      )}

      <AlertDialog open={!!toDelete} onOpenChange={(o) => !o && setToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-base">
              Delete "{toDelete?.name}"?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-xs">
              RivalTracking will stop watching for this activity. Alerts already
              triggered by this rule are kept.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="h-9 text-xs font-semibold">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (toDelete) onDeleteRule(toDelete.id)
                setToDelete(null)
              }}
              className="h-9 bg-destructive text-xs font-bold text-destructive-foreground hover:bg-destructive/90"
            >
              Delete alert
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  )
}
