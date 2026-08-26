import { createContext, useContext, useMemo, useState, type ReactNode } from "react"

import * as alertService from "@/services/alerts"
import {
  alertRules as initialRules,
  initialRecentAlerts,
  type AlertRule,
  type RecentAlert,
} from "@/lib/alerts-data"

/* Session-level alert state shared by the sidebar badge, the Alerts page
   and every "create alert" entry point. The backend equivalents are
   GET/POST/PATCH/DELETE /api/alerts/rules, POST /api/alerts/:id/read and
   POST /api/alerts/read-all. */

type AlertsContextValue = {
  recentAlerts: RecentAlert[]
  unreadCount: number
  markRead: (id: number) => void
  markAllRead: () => void
  alertRules: AlertRule[]
  createRule: (rule: AlertRule) => Promise<AlertRule>
  updateRule: (rule: AlertRule) => Promise<void>
  toggleRule: (id: string) => void
  duplicateRule: (id: string) => Promise<AlertRule | null>
  deleteRule: (id: string) => Promise<void>
  /* Returns an id not currently taken by any rule (appends -2, -3, ...). */
  uniqueRuleId: (base: string) => string
}

const AlertsContext = createContext<AlertsContextValue | null>(null)

export function AlertsProvider({ children }: { children: ReactNode }) {
  const [recentAlerts, setRecentAlerts] = useState<RecentAlert[]>(initialRecentAlerts)
  const [alertRules, setAlertRules] = useState<AlertRule[]>(initialRules)

  const value = useMemo<AlertsContextValue>(() => {
    const uniqueRuleId = (base: string) => {
      if (!alertRules.some((r) => r.id === base)) return base
      let n = 2
      while (alertRules.some((r) => r.id === `${base}-${n}`)) n += 1
      return `${base}-${n}`
    }

    return {
      recentAlerts,
      unreadCount: recentAlerts.filter((a) => a.status === "new").length,
      markRead: (id) => {
        setRecentAlerts((prev) =>
          prev.map((a) => (a.id === id ? { ...a, status: "viewed" } : a))
        )
        void alertService.markRead(id)
      },
      markAllRead: () => {
        setRecentAlerts((prev) => prev.map((a) => ({ ...a, status: "viewed" })))
        void alertService.markAllRead()
      },
      alertRules,
      uniqueRuleId,
      createRule: async (rule) => {
        const safeRule = { ...rule, id: uniqueRuleId(rule.id) }
        await alertService.createRule(safeRule)
        setAlertRules((prev) => [safeRule, ...prev])
        return safeRule
      },
      updateRule: async (rule) => {
        await alertService.updateRule(rule)
        setAlertRules((prev) => prev.map((r) => (r.id === rule.id ? rule : r)))
      },
      toggleRule: (id) =>
        setAlertRules((prev) =>
          prev.map((r) => (r.id === id ? { ...r, active: !r.active } : r))
        ),
      duplicateRule: async (id) => {
        const source = alertRules.find((r) => r.id === id)
        if (!source) return null
        const copy: AlertRule = {
          ...source,
          id: uniqueRuleId(`${source.id}-copy`),
          name: `${source.name} (copy)`,
          lastTriggered: "Never",
          createdAt: new Date().toISOString().slice(0, 10),
        }
        await alertService.createRule(copy)
        setAlertRules((prev) => [copy, ...prev])
        return copy
      },
      deleteRule: async (id) => {
        await alertService.deleteRule(id)
        setAlertRules((prev) => prev.filter((r) => r.id !== id))
      },
    }
  }, [recentAlerts, alertRules])

  return <AlertsContext.Provider value={value}>{children}</AlertsContext.Provider>
}

export function useAlerts() {
  const ctx = useContext(AlertsContext)
  if (!ctx) throw new Error("useAlerts must be used within AlertsProvider")
  return ctx
}
