import { useNavigate } from "react-router-dom"
import {
  Baby,
  BellOff,
  Bike,
  Blocks,
  Bot,
  Check,
  CheckCheck,
  Eye,
  GitCompareArrows,
  MoreHorizontal,
  Package,
  type LucideIcon,
} from "lucide-react"

import { type RecentAlert } from "@/lib/alerts-data"
import { useAlerts } from "@/lib/alerts-store"
import { cn } from "@/lib/utils"
import { useIsMobile } from "@/hooks/use-mobile"
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
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { ChangeBadge } from "@/components/shared/change-badge"
import { EmptyState } from "@/components/shared/empty-state"
import { ImpactBadge } from "@/components/shared/impact-badge"
import { NotificationStatusBadge } from "@/components/alerts/alert-status-badge"

const productIcons: Record<string, LucideIcon> = {
  "lego-castle-set": Blocks,
  "stem-robot-kit": Bot,
  "wooden-balance-bike": Bike,
  "stem-coding-kit": Bot,
  "garden-water-table": Baby,
}

function SubjectCell({ alert }: { alert: RecentAlert }) {
  if (alert.isPattern) {
    return (
      <span className="flex items-center gap-2.5">
        <span className="flex size-8.5 shrink-0 items-center justify-center rounded-lg bg-teal/10 text-teal">
          <GitCompareArrows className="size-4" />
        </span>
        <span className="min-w-0">
          <span className="block truncate text-sm font-medium text-foreground">
            {alert.patternLabel}
          </span>
          <span className="mt-0.5 block text-[11px] text-muted-foreground">
            Change pattern{alert.category ? ` · ${alert.category}` : ""}
          </span>
        </span>
      </span>
    )
  }
  const Icon = productIcons[alert.productSlug ?? ""] ?? Package
  return (
    <span className="flex items-center gap-2.5">
      <span className="flex size-8.5 shrink-0 items-center justify-center rounded-lg bg-accent text-accent-foreground">
        <Icon className="size-4" />
      </span>
      <span className="min-w-0">
        <span className="block truncate text-sm font-medium text-foreground">
          {alert.product}
        </span>
        <span className="mt-0.5 block text-[11px] text-muted-foreground">
          Product
        </span>
      </span>
    </span>
  )
}

function AlertRowActions({
  alert,
  onOpen,
}: {
  alert: RecentAlert
  onOpen: () => void
}) {
  const navigate = useNavigate()
  const { markRead } = useAlerts()
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="size-7 text-muted-foreground"
          onClick={(e) => e.stopPropagation()}
        >
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
        <DropdownMenuItem onClick={onOpen}>
          <Eye className="size-3.5" /> View details
        </DropdownMenuItem>
        {alert.isPattern ? (
          <DropdownMenuItem onClick={() => navigate("/changes")}>
            <GitCompareArrows className="size-3.5" /> View pattern
          </DropdownMenuItem>
        ) : (
          <DropdownMenuItem
            onClick={() => navigate(`/products/${alert.productSlug}`)}
          >
            <Package className="size-3.5" /> View product
          </DropdownMenuItem>
        )}
        {alert.status === "new" && (
          <DropdownMenuItem onClick={() => markRead(alert.id)}>
            <Check className="size-3.5" /> Mark as read
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export function RecentAlertsTable({
  onOpenDetails,
  filterRule = null,
  onClearRuleFilter,
}: {
  onOpenDetails: (alert: RecentAlert) => void
  /* When set ("View history" on a rule), only that rule's alerts show. */
  filterRule?: { id: string; name: string } | null
  onClearRuleFilter?: () => void
}) {
  const isMobile = useIsMobile()
  const { recentAlerts: allAlerts, unreadCount, markAllRead, markRead } = useAlerts()

  const recentAlerts = filterRule
    ? allAlerts.filter((a) => a.ruleId === filterRule.id)
    : allAlerts

  const open = (alert: RecentAlert) => {
    markRead(alert.id)
    onOpenDetails(alert)
  }

  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-bold">Recent Alerts</CardTitle>
        {filterRule && (
          <p className="flex items-center gap-2 text-xs text-muted-foreground">
            Showing history for “{filterRule.name}”
            <button
              onClick={onClearRuleFilter}
              className="text-[11px] font-bold text-primary"
            >
              Show all
            </button>
          </p>
        )}
        <CardAction>
          <Button
            variant="outline"
            size="sm"
            onClick={markAllRead}
            disabled={unreadCount === 0}
            className="h-8 rounded-lg text-[11px] font-bold"
          >
            <CheckCheck className="size-3.5" /> Mark all as read
          </Button>
        </CardAction>
      </CardHeader>

      {recentAlerts.length === 0 ? (
        <EmptyState
          icon={BellOff}
          heading="No alerts triggered yet"
          text="RivalTracking will notify you when competitor activity matches one of your rules."
        />
      ) : isMobile ? (
        <CardContent className="flex flex-col gap-3 px-4 pb-4">
          {recentAlerts.map((a) => (
            <div
              key={a.id}
              onClick={() => open(a)}
              className={cn(
                "cursor-pointer rounded-xl border p-3.5",
                a.status === "new" && "bg-accent/40"
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <SubjectCell alert={a} />
                </div>
                <AlertRowActions alert={a} onOpen={() => open(a)} />
              </div>
              <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                <ChangeBadge kind={a.kind} label={a.event} />
                <ImpactBadge impact={a.priority} />
                <NotificationStatusBadge status={a.status} />
              </div>
              <p className="mt-2 text-[11px] text-muted-foreground">
                {a.ruleName} · {a.competitor} · {a.triggered}
              </p>
            </div>
          ))}
        </CardContent>
      ) : (
        <CardContent className="px-0 pb-0">
          <div className="overflow-x-auto">
            <Table className="min-w-[1020px]">
              <TableHeader>
                <TableRow>
                  {[
                    "Alert",
                    "Event",
                    "Competitor",
                    "Product / Pattern",
                    "Priority",
                    "Triggered",
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
                {recentAlerts.map((a) => (
                  <TableRow
                    key={a.id}
                    onClick={() => open(a)}
                    className={cn(
                      "cursor-pointer text-[11px] text-muted-foreground",
                      a.status === "new" && "bg-accent/40"
                    )}
                  >
                    <TableCell className="max-w-48 truncate px-3.5 text-sm font-medium text-foreground">
                      {a.ruleName}
                    </TableCell>
                    <TableCell className="px-3.5">
                      <ChangeBadge kind={a.kind} label={a.event} />
                    </TableCell>
                    <TableCell className="px-3.5">{a.competitor}</TableCell>
                    <TableCell className="px-3.5 py-2.5">
                      <SubjectCell alert={a} />
                    </TableCell>
                    <TableCell className="px-3.5">
                      <ImpactBadge impact={a.priority} />
                    </TableCell>
                    <TableCell className="px-3.5 whitespace-nowrap">
                      {a.triggered}
                    </TableCell>
                    <TableCell className="px-3.5">
                      <NotificationStatusBadge status={a.status} />
                    </TableCell>
                    <TableCell className="px-2 text-right">
                      <AlertRowActions alert={a} onOpen={() => open(a)} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      )}
    </Card>
  )
}
