import { weeklyReport, type GeneratedReport } from "@/lib/reports-data"

/* Client-side CSV of a report's structured metrics. The real export will
   come from the Report Engine backend; until then the detailed weekly
   dataset serves as the mock body for every report. */
export function reportCsv(report: GeneratedReport): {
  filename: string
  headers: string[]
  rows: (string | number)[][]
} {
  const meta: (string | number)[][] = [
    ["Report", report.name],
    ["Type", report.type],
    ["Competitors", report.competitors],
    ["Period", report.period],
    ["Data through", report.dataThrough],
    [],
  ]
  const metrics = weeklyReport.metrics.map((m) => ["Metric", m.label, m.value])
  const comparison = weeklyReport.competitorComparison.map((c) => [
    "Competitor",
    c.name,
    `changes=${c.total}`,
    `new=${c.newProducts}`,
    `drops=${c.drops}`,
    `increases=${c.increases}`,
    `stockouts=${c.stockouts}`,
    `promos=${c.promos}`,
  ])
  return {
    filename: `competeiq-report-${report.id}.csv`,
    headers: ["Section", "Item", "Value", "", "", "", "", ""],
    rows: [...meta, ...metrics, ...comparison],
  }
}
