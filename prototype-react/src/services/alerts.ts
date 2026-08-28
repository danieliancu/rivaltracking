import { mockOk } from "@/services/mock"
import type { AlertRule } from "@/lib/alerts-data"

/** Future: POST /api/alerts/rules */
export function createRule(rule: AlertRule): Promise<AlertRule> {
  return mockOk(rule, 400)
}

/** Future: PATCH /api/alerts/rules/:id */
export function updateRule(rule: AlertRule): Promise<AlertRule> {
  return mockOk(rule, 400)
}

/** Future: DELETE /api/alerts/rules/:id */
export function deleteRule(id: string): Promise<{ id: string }> {
  return mockOk({ id }, 300)
}

/** Future: POST /api/alerts/:id/read */
export function markRead(id: number): Promise<{ id: number }> {
  return mockOk({ id }, 150)
}

/** Future: POST /api/alerts/read-all */
export function markAllRead(): Promise<void> {
  return mockOk(undefined, 150)
}
