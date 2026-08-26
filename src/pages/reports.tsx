import { useEffect, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import {
  BadgeCheck,
  CalendarClock,
  FileBarChart2,
  Plus,
  Settings2,
  Users,
  type LucideIcon,
} from "lucide-react"
import { toast } from "sonner"

import { reportFormOptions, reportKpis, type GeneratedReport } from "@/lib/reports-data"
import { reportCsv } from "@/lib/report-csv"
import { downloadCsv } from "@/lib/csv"
import { useWorkspace } from "@/lib/workspace-store"
import { Button } from "@/components/ui/button"
import { KpiCard, type KpiTone } from "@/components/shared/kpi-card"
import {
  CreateReportDialog,
  type ReportPrefill,
} from "@/components/reports/create-report-dialog"
import { GeneratedReportsTable } from "@/components/reports/generated-reports-table"
import { ReportLibrary } from "@/components/reports/report-library"
import { ScheduledReports } from "@/components/reports/scheduled-reports"

const kpiIcons: Record<string, LucideIcon> = {
  generated: FileBarChart2,
  scheduled: CalendarClock,
  covered: Users,
  latest: BadgeCheck,
}

export function ReportsPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { reports, deleteReport } = useWorkspace()
  const [createOpen, setCreateOpen] = useState(false)
  const [initialTypeId, setInitialTypeId] = useState<string | null>(null)
  const [prefill, setPrefill] = useState<ReportPrefill | null>(null)
  const [scheduleTypeId, setScheduleTypeId] = useState<string | null>(null)

  /* "Create report" handed over from Ask AI. */
  useEffect(() => {
    const state = location.state as {
      createReport?: { typeId?: string | null }
    } | null
    if (!state?.createReport) return
    setPrefill(null)
    setInitialTypeId(state.createReport.typeId ?? null)
    setCreateOpen(true)
    navigate(location.pathname, { replace: true })
  }, [location, navigate])

  const openCreate = (typeId: string | null = null) => {
    setPrefill(null)
    setInitialTypeId(typeId)
    setCreateOpen(true)
  }

  const duplicate = (report: GeneratedReport) => {
    setInitialTypeId(null)
    setPrefill({
      typeId: report.typeId,
      competitors:
        report.competitors === "All"
          ? reportFormOptions.competitors[0]
          : report.competitors,
      dateRange: reportFormOptions.dateRanges.includes(report.period)
        ? report.period
        : undefined,
      category: report.category,
      changeType: report.changeType,
      aiAnalysis: report.aiAnalysis,
    })
    setCreateOpen(true)
  }

  const exportCsv = (report: GeneratedReport) => {
    const csv = reportCsv(report)
    downloadCsv(csv.filename, csv.headers, csv.rows)
    toast.success("Export ready", { description: `${report.name} exported to CSV.` })
  }

  const downloadPdf = (report: GeneratedReport) => {
    toast.info("PDF generation will be handled by the report backend.", {
      description: `${report.name} can be exported to CSV in the meantime.`,
    })
  }

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <section className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">Reports</h1>
          <p className="mt-1 text-xs text-muted-foreground">
            Turn competitor activity into clear, actionable intelligence.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => navigate("/settings/reports")}
            className="h-9 rounded-lg bg-card text-xs font-bold"
          >
            <Settings2 className="size-4" /> Report settings
          </Button>
          <Button
            onClick={() => openCreate()}
            className="h-9 rounded-lg text-xs font-bold shadow-md shadow-primary/25"
          >
            <Plus className="size-4" /> Create report
          </Button>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-3.5 xl:grid-cols-4">
        {reportKpis.map((k) => (
          <KpiCard
            key={k.id}
            icon={kpiIcons[k.id]}
            tone={k.tone as KpiTone}
            value={k.value}
            label={k.label}
          />
        ))}
      </section>

      <ReportLibrary onSelectType={(t) => openCreate(t.id)} />

      <GeneratedReportsTable
        reports={reports}
        onDeleteReport={async (id) => {
          const name = reports.find((r) => r.id === id)?.name
          await deleteReport(id)
          toast.info("Report deleted", { description: name })
        }}
        onCreate={() => openCreate()}
        onDownloadPdf={downloadPdf}
        onExportCsv={exportCsv}
        onDuplicate={duplicate}
        onSchedule={(report) => setScheduleTypeId(report.typeId)}
      />

      <ScheduledReports
        scheduleTypeId={scheduleTypeId}
        onScheduleTypeConsumed={() => setScheduleTypeId(null)}
      />

      <CreateReportDialog
        open={createOpen}
        initialTypeId={initialTypeId}
        prefill={prefill}
        onOpenChange={setCreateOpen}
        onView={(id) => navigate(`/reports/${id}`)}
      />
    </main>
  )
}
