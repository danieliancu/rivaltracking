import { useEffect, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import {
  Bell,
  BellRing,
  Plus,
  TriangleAlert,
  Users,
  type LucideIcon,
} from "lucide-react"
import { toast } from "sonner"

import { alertKpis, type AlertRule, type RecentAlert } from "@/lib/alerts-data"
import { useAlerts } from "@/lib/alerts-store"
import { Button } from "@/components/ui/button"
import { AIInsightCard } from "@/components/shared/ai-insight-card"
import { KpiCard, type KpiTone } from "@/components/shared/kpi-card"
import { AlertActivity } from "@/components/alerts/alert-activity"
import { AlertCoverage } from "@/components/alerts/alert-coverage"
import { AlertDetailDrawer } from "@/components/alerts/alert-detail-drawer"
import { AlertRulesTable } from "@/components/alerts/alert-rules-table"
import {
  CreateAlertDialog,
  type AlertPrefill,
} from "@/components/alerts/create-alert-dialog"
import { MostTriggeredRules } from "@/components/alerts/most-triggered-rules"
import { RecentAlertsTable } from "@/components/alerts/recent-alerts-table"

const kpiIcons: Record<string, LucideIcon> = {
  active: Bell,
  triggered: BellRing,
  high: TriangleAlert,
  covered: Users,
}

/* Map a Changes-page change-type filter onto a create-alert trigger. */
const kindToTrigger: Record<string, string> = {
  drop: "price-decrease",
  increase: "price-increase",
  oos: "stock-out",
  back: "stock-back",
  new: "product-new",
  removed: "product-removed",
  promo: "promo-start",
  "promo-end": "promo-end",
}

export function AlertsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const {
    alertRules,
    createRule,
    updateRule,
    toggleRule,
    duplicateRule,
    deleteRule,
  } = useAlerts()
  const [createOpen, setCreateOpen] = useState(false)
  const [prefill, setPrefill] = useState<AlertPrefill | null>(null)
  const [editRule, setEditRule] = useState<AlertRule | null>(null)
  const [detailAlert, setDetailAlert] = useState<RecentAlert | null>(null)
  const [historyRule, setHistoryRule] = useState<{ id: string; name: string } | null>(
    null
  )

  useEffect(() => {
    const state = location.state as {
      createAlert?: {
        competitor?: string
        kind?: string
        category?: string
        product?: string
      }
    } | null
    if (!state?.createAlert) return
    const { competitor, kind, category, product } = state.createAlert
    setEditRule(null)
    setPrefill({
      competitor:
        competitor && competitor !== "All competitors" ? competitor : undefined,
      triggerId: kind && kind !== "all" ? kindToTrigger[kind] : undefined,
      category:
        category && category !== "All categories" ? category : undefined,
      product,
    })
    setCreateOpen(true)
    /* Clear the router state so a refresh does not reopen the dialog. */
    navigate(location.pathname, { replace: true })
  }, [location, navigate])

  const openCreate = () => {
    setPrefill(null)
    setEditRule(null)
    setCreateOpen(true)
  }

  const openEdit = (rule: AlertRule) => {
    setPrefill(null)
    setEditRule(rule)
    setCreateOpen(true)
  }

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <section className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">Alerts</h1>
          <p className="mt-1 text-xs text-muted-foreground">
            Get notified when important competitor activity matches your rules.
          </p>
        </div>
        <Button
          onClick={openCreate}
          className="h-9 rounded-lg text-xs font-bold shadow-md shadow-primary/25"
        >
          <Plus className="size-4" /> Create alert
        </Button>
      </section>

      <section className="grid grid-cols-2 gap-3.5 xl:grid-cols-4">
        {alertKpis.map((k) => (
          <KpiCard
            key={k.id}
            icon={kpiIcons[k.id]}
            tone={k.tone as KpiTone}
            value={k.value}
            label={k.label}
          />
        ))}
      </section>

      <AIInsightCard
        title="Alert Intelligence"
        ctaLabel="View related changes"
        onCta={() => navigate("/changes")}
      >
        Most alerts triggered today relate to{" "}
        <strong className="text-foreground">ToyWorld.co.uk</strong> pricing
        activity. <strong className="text-foreground">Outdoor Toys</strong>{" "}
        generated 8 alerts after multiple products fell more than 10% in price.
        One high-priority stock alert was also triggered for Educational Toys.
      </AIInsightCard>

      <AlertRulesTable
        rules={alertRules}
        onToggleRule={(id) => {
          const rule = alertRules.find((r) => r.id === id)
          toggleRule(id)
          if (rule)
            toast.info(rule.active ? "Alert paused" : "Alert resumed", {
              description: rule.name,
            })
        }}
        onDeleteRule={async (id) => {
          const name = alertRules.find((r) => r.id === id)?.name
          await deleteRule(id)
          toast.info("Alert deleted", { description: name })
        }}
        onCreate={openCreate}
        onEditRule={openEdit}
        onDuplicateRule={async (rule) => {
          const copy = await duplicateRule(rule.id)
          if (copy) toast.success("Alert duplicated", { description: copy.name })
        }}
        onViewHistory={(rule) => setHistoryRule({ id: rule.id, name: rule.name })}
      />

      <RecentAlertsTable
        onOpenDetails={setDetailAlert}
        filterRule={historyRule}
        onClearRuleFilter={() => setHistoryRule(null)}
      />

      <section className="grid gap-4 xl:grid-cols-[2fr_1fr] xl:items-start">
        <AlertActivity />
        <div className="flex flex-col gap-4">
          <MostTriggeredRules />
          <AlertCoverage />
        </div>
      </section>

      <CreateAlertDialog
        open={createOpen}
        prefill={prefill}
        editRule={editRule}
        onOpenChange={setCreateOpen}
        onCreated={async (rule) => {
          if (editRule) {
            await updateRule(rule)
            toast.success("Alert updated", { description: rule.name })
          } else {
            const created = await createRule(rule)
            toast.success("Alert created", { description: created.name })
          }
        }}
      />
      <AlertDetailDrawer
        alert={detailAlert}
        onClose={() => setDetailAlert(null)}
        onEditRule={(ruleId) => {
          const rule = alertRules.find((r) => r.id === ruleId)
          if (rule) openEdit(rule)
        }}
      />
    </main>
  )
}
