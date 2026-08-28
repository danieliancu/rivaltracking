import { mockOk } from "@/services/mock"
import type { GeneratedReport, ReportSchedule } from "@/lib/reports-data"

export type ReportInput = {
  typeId: string
  type: string
  competitors: string
  period: string
  category?: string
  changeType?: string
  aiAnalysis: boolean
}

/** Future: POST /api/reports → GeneratedReport (Report Engine + analytics). */
export function generateReport(input: ReportInput, id: string): Promise<GeneratedReport> {
  return mockOk(
    {
      id,
      name: `${input.type} — ${input.period}`,
      typeId: input.typeId,
      type: input.type,
      competitors: input.competitors,
      period: input.period,
      created: "Just now",
      status: "ready",
      dataThrough: "26 Aug, 14:42",
      category: input.category,
      changeType: input.changeType,
      aiAnalysis: input.aiAnalysis,
    },
    400
  )
}

/** Future: DELETE /api/reports/:id */
export function deleteReport(id: string): Promise<{ id: string }> {
  return mockOk({ id }, 300)
}

/** Future: POST /api/report-schedules and PATCH /api/report-schedules/:id */
export function saveSchedule(schedule: ReportSchedule): Promise<ReportSchedule> {
  return mockOk(schedule, 400)
}

/** Future: DELETE /api/report-schedules/:id */
export function deleteSchedule(id: string): Promise<{ id: string }> {
  return mockOk({ id }, 300)
}
