import { useState } from "react"
import { useNavigate } from "react-router-dom"
import {
  CalendarClock,
  Copy,
  Download,
  Eye,
  FileText,
  MoreHorizontal,
  Plus,
  Trash2,
} from "lucide-react"

import {
  reportTypes,
  type GeneratedReport,
} from "@/lib/reports-data"
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { EmptyState } from "@/components/shared/empty-state"
import { ReportStatusBadge } from "@/components/reports/report-status-badge"

function ReportName({ report }: { report: GeneratedReport }) {
  const type = reportTypes.find((t) => t.id === report.typeId)
  const Icon = type?.icon ?? FileText
  return (
    <div className="flex items-center gap-2.5">
      <span
        className={cn(
          "flex size-8.5 shrink-0 items-center justify-center rounded-lg",
          type?.tone ?? "bg-muted text-muted-foreground"
        )}
      >
        <Icon className="size-4" />
      </span>
      <span className="min-w-0">
        <span className="block truncate text-sm font-medium text-foreground">
          {report.name}
        </span>
        <span className="mt-0.5 block text-[11px] text-muted-foreground">
          Data through: {report.dataThrough}
        </span>
      </span>
    </div>
  )
}

function RowActions({
  report,
  onView,
  onDelete,
  onDownloadPdf,
  onExportCsv,
  onDuplicate,
  onSchedule,
}: {
  report: GeneratedReport
  onView: () => void
  onDelete: () => void
  onDownloadPdf: () => void
  onExportCsv: () => void
  onDuplicate: () => void
  onSchedule: () => void
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Actions for ${report.name}`}
          className="size-7 text-muted-foreground"
          onClick={(e) => e.stopPropagation()}
        >
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
        <DropdownMenuItem
          onClick={onView}
          disabled={report.status !== "ready"}
        >
          <Eye className="size-3.5" /> View report
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={onDownloadPdf}
          disabled={report.status !== "ready"}
        >
          <Download className="size-3.5" /> Download PDF
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={onExportCsv}
          disabled={report.status !== "ready"}
        >
          <FileText className="size-3.5" /> Export CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onDuplicate}>
          <Copy className="size-3.5" /> Duplicate
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onSchedule}>
          <CalendarClock className="size-3.5" /> Schedule
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem variant="destructive" onClick={onDelete}>
          <Trash2 className="size-3.5" /> Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export function GeneratedReportsTable({
  reports,
  onDeleteReport,
  onCreate,
  onDownloadPdf,
  onExportCsv,
  onDuplicate,
  onSchedule,
}: {
  reports: GeneratedReport[]
  onDeleteReport: (id: string) => void
  onCreate: () => void
  onDownloadPdf: (report: GeneratedReport) => void
  onExportCsv: (report: GeneratedReport) => void
  onDuplicate: (report: GeneratedReport) => void
  onSchedule: (report: GeneratedReport) => void
}) {
  const navigate = useNavigate()
  const isMobile = useIsMobile()
  const [toDelete, setToDelete] = useState<GeneratedReport | null>(null)

  const view = (report: GeneratedReport) => {
    if (report.status === "ready") navigate(`/reports/${report.id}`)
  }

  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-bold">Generated Reports</CardTitle>
      </CardHeader>

      {reports.length === 0 ? (
        <EmptyState
          icon={FileText}
          heading="No reports yet"
          text="Create your first intelligence report from the competitor data RivalTracking has collected."
          actionLabel="Create report"
          onAction={onCreate}
        />
      ) : isMobile ? (
        <CardContent className="flex flex-col gap-3 px-4 pb-4">
          {reports.map((r) => (
            <div
              key={r.id}
              onClick={() => view(r)}
              className={cn(
                "rounded-xl border p-3.5",
                r.status === "ready" && "cursor-pointer"
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <ReportName report={r} />
                </div>
                <RowActions
                  report={r}
                  onView={() => view(r)}
                  onDelete={() => setToDelete(r)}
                  onDownloadPdf={() => onDownloadPdf(r)}
                  onExportCsv={() => onExportCsv(r)}
                  onDuplicate={() => onDuplicate(r)}
                  onSchedule={() => onSchedule(r)}
                />
              </div>
              <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                <ReportStatusBadge status={r.status} />
                <span className="text-[11px] text-muted-foreground">
                  {r.type} · {r.period} · {r.created}
                </span>
              </div>
              {r.note && (
                <p className="mt-2 text-[11px] text-muted-foreground">{r.note}</p>
              )}
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
                    "Report",
                    "Type",
                    "Competitors",
                    "Period",
                    "Created",
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
                {reports.map((r) => (
                  <TableRow
                    key={r.id}
                    onClick={() => view(r)}
                    className={cn(
                      "text-[11px] text-muted-foreground",
                      r.status === "ready" && "cursor-pointer"
                    )}
                  >
                    <TableCell className="px-3.5 py-2.5">
                      <ReportName report={r} />
                    </TableCell>
                    <TableCell className="px-3.5">{r.type}</TableCell>
                    <TableCell className="px-3.5">{r.competitors}</TableCell>
                    <TableCell className="px-3.5">{r.period}</TableCell>
                    <TableCell className="px-3.5 whitespace-nowrap">
                      {r.created}
                    </TableCell>
                    <TableCell className="px-3.5">
                      <span>
                        <ReportStatusBadge status={r.status} />
                        {r.note && (
                          <span className="mt-1 block max-w-52 text-[11px]">
                            {r.note}
                          </span>
                        )}
                      </span>
                    </TableCell>
                    <TableCell className="px-2 text-right">
                      <RowActions
                        report={r}
                        onView={() => view(r)}
                        onDelete={() => setToDelete(r)}
                        onDownloadPdf={() => onDownloadPdf(r)}
                        onExportCsv={() => onExportCsv(r)}
                        onDuplicate={() => onDuplicate(r)}
                        onSchedule={() => onSchedule(r)}
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
              Delete {toDelete?.name}?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-xs">
              This report and its generated intelligence will be permanently
              removed. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="h-9 text-xs font-semibold">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (toDelete) onDeleteReport(toDelete.id)
                setToDelete(null)
              }}
              className="h-9 bg-destructive text-xs font-bold text-destructive-foreground hover:bg-destructive/90"
            >
              Delete report
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {reports.length > 0 && (
        <div className="border-t p-0">
          <Button
            variant="ghost"
            onClick={onCreate}
            className="h-11 w-full rounded-none text-[11px] font-bold text-primary"
          >
            <Plus className="size-3.5" /> Create report
          </Button>
        </div>
      )}
    </Card>
  )
}
