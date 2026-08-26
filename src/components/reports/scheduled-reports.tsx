import { useEffect, useState } from "react"
import {
  CalendarClock,
  MoreHorizontal,
  Pause,
  Pencil,
  Play,
  Plus,
  Trash2,
} from "lucide-react"
import { toast } from "sonner"

import { reportTypes, type ReportSchedule } from "@/lib/reports-data"
import { useWorkspace } from "@/lib/workspace-store"
import { cn } from "@/lib/utils"
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
import { EmptyState } from "@/components/shared/empty-state"
import { ScheduleReportDialog } from "@/components/reports/schedule-report-dialog"

export function ScheduledReports({
  scheduleTypeId = null,
  onScheduleTypeConsumed,
}: {
  /* When set (by "Schedule" on a generated report), opens the dialog
     preselected to that report type. */
  scheduleTypeId?: string | null
  onScheduleTypeConsumed?: () => void
}) {
  const { reportSchedules, saveSchedule, toggleSchedule, deleteSchedule } =
    useWorkspace()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editSchedule, setEditSchedule] = useState<ReportSchedule | null>(null)
  const [initialTypeId, setInitialTypeId] = useState<string | null>(null)
  const [toDelete, setToDelete] = useState<ReportSchedule | null>(null)

  useEffect(() => {
    if (!scheduleTypeId) return
    setEditSchedule(null)
    setInitialTypeId(scheduleTypeId)
    setDialogOpen(true)
    onScheduleTypeConsumed?.()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scheduleTypeId])

  const openNew = () => {
    setEditSchedule(null)
    setInitialTypeId(null)
    setDialogOpen(true)
  }

  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-bold">Scheduled Reports</CardTitle>
        <CardAction>
          <Button
            variant="outline"
            size="sm"
            onClick={openNew}
            className="h-8 rounded-lg text-[11px] font-bold"
          >
            <CalendarClock className="size-3.5" /> Schedule report
          </Button>
        </CardAction>
      </CardHeader>

      {reportSchedules.length === 0 && (
        <EmptyState
          icon={CalendarClock}
          heading="No scheduled reports"
          text="Schedule a report and CompeteIQ will generate it automatically."
          actionLabel="Schedule report"
          onAction={openNew}
        />
      )}

      {reportSchedules.map((s) => {
        const type = reportTypes.find((t) => t.id === s.typeId)
        const Icon = type?.icon ?? CalendarClock
        return (
          <div key={s.id} className="flex items-center gap-2.5 border-t px-5 py-3">
            <span
              className={cn(
                "flex size-8.5 shrink-0 items-center justify-center rounded-lg",
                type?.tone ?? "bg-muted text-muted-foreground"
              )}
            >
              <Icon className="size-4" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-medium">
                {s.name}
              </span>
              <span className="mt-0.5 block truncate text-[11px] text-muted-foreground">
                {s.frequency} · {s.time} · {s.competitors}
              </span>
            </span>
            <Badge
              variant="outline"
              className={cn(
                "gap-1.5 rounded-full px-2 py-1 text-[11px] font-bold",
                s.active
                  ? "border-success/25 bg-success/10 text-success"
                  : "border-border bg-muted text-muted-foreground"
              )}
            >
              <i
                className={cn(
                  "size-1.5 rounded-full",
                  s.active ? "bg-success" : "bg-muted-foreground"
                )}
              />
              {s.active ? "Active" : "Paused"}
            </Badge>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`Actions for ${s.name} schedule`}
                  className="size-7 text-muted-foreground"
                >
                  <MoreHorizontal className="size-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={() => {
                    setEditSchedule(s)
                    setInitialTypeId(null)
                    setDialogOpen(true)
                  }}
                >
                  <Pencil className="size-3.5" /> Edit
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => {
                    toggleSchedule(s.id)
                    toast.info(s.active ? "Schedule paused" : "Schedule resumed", {
                      description: s.name,
                    })
                  }}
                >
                  {s.active ? (
                    <>
                      <Pause className="size-3.5" /> Pause
                    </>
                  ) : (
                    <>
                      <Play className="size-3.5" /> Resume
                    </>
                  )}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  variant="destructive"
                  onClick={() => setToDelete(s)}
                >
                  <Trash2 className="size-3.5" /> Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )
      })}

      <div className="border-t p-0">
        <Button
          variant="ghost"
          onClick={openNew}
          className="h-11 w-full rounded-none text-[11px] font-bold text-primary"
        >
          <Plus className="size-3.5" /> Schedule report
        </Button>
      </div>

      <ScheduleReportDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        schedule={editSchedule}
        initialTypeId={initialTypeId}
        onScheduled={async (s) => {
          await saveSchedule(s)
          toast.success(editSchedule ? "Schedule updated" : "Report scheduled", {
            description: `${s.name} · ${s.frequency} at ${s.time}`,
          })
        }}
      />

      <AlertDialog open={!!toDelete} onOpenChange={(o) => !o && setToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-base">
              Delete scheduled report?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-xs">
              {toDelete?.name} will no longer be generated automatically.
              Already generated reports are not affected.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="h-9 text-xs font-semibold">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={async () => {
                if (toDelete) {
                  await deleteSchedule(toDelete.id)
                  toast.info("Schedule deleted", { description: toDelete.name })
                }
                setToDelete(null)
              }}
              className="h-9 bg-destructive text-xs font-bold text-destructive-foreground hover:bg-destructive/90"
            >
              Delete schedule
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  )
}
