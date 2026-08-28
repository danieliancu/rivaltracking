import { useEffect, useState } from "react"

import {
  reportFormOptions,
  reportTypes,
  type ReportSchedule,
} from "@/lib/reports-data"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const frequencyLabels: Record<string, string> = {
  Daily: "Every day",
  Weekly: "Every Monday",
  Monthly: "Every month",
}

export function ScheduleReportDialog({
  open,
  onOpenChange,
  onScheduled,
  initialTypeId = null,
  schedule = null,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onScheduled: (schedule: ReportSchedule) => void
  /* Preselect a report type (e.g. "Schedule" from a generated report). */
  initialTypeId?: string | null
  /* Edit an existing schedule in place. */
  schedule?: ReportSchedule | null
}) {
  const [typeId, setTypeId] = useState(reportTypes[0].id)
  const [competitors, setCompetitors] = useState(reportFormOptions.competitors[0])
  const [frequency, setFrequency] = useState("Daily")
  const [time, setTime] = useState("08:00")

  useEffect(() => {
    if (!open) return
    if (schedule) {
      setTypeId(schedule.typeId)
      setCompetitors(
        reportFormOptions.competitors.includes(schedule.competitors)
          ? schedule.competitors
          : reportFormOptions.competitors[0]
      )
      setFrequency(
        Object.entries(frequencyLabels).find(
          ([, label]) => label === schedule.frequency
        )?.[0] ?? "Daily"
      )
      setTime(schedule.time)
    } else {
      setTypeId(initialTypeId ?? reportTypes[0].id)
      setCompetitors(reportFormOptions.competitors[0])
      setFrequency("Daily")
      setTime("08:00")
    }
  }, [open, schedule, initialTypeId])

  const save = () => {
    const type = reportTypes.find((t) => t.id === typeId) ?? reportTypes[0]
    onScheduled({
      id: schedule?.id ?? `s-${typeId}-${Date.now().toString(36)}`,
      name: type.title,
      typeId: type.id,
      frequency: frequencyLabels[frequency] ?? "Every day",
      time,
      competitors:
        competitors === reportFormOptions.competitors[0]
          ? "All competitors"
          : competitors,
      active: schedule?.active ?? true,
    })
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle className="text-base font-bold">
            {schedule ? "Edit scheduled report" : "Schedule report"}
          </DialogTitle>
          <DialogDescription className="text-xs">
            RivalTracking will generate this report automatically.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-3.5">
          <div className="flex flex-col gap-1.5">
            <Label className="text-xs font-semibold">Report</Label>
            <Select value={typeId} onValueChange={setTypeId}>
              <SelectTrigger className="h-9 w-full text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {reportTypes.map((t) => (
                  <SelectItem key={t.id} value={t.id} className="text-xs">
                    {t.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label className="text-xs font-semibold">Competitors</Label>
            <Select value={competitors} onValueChange={setCompetitors}>
              <SelectTrigger className="h-9 w-full text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {reportFormOptions.competitors.map((c) => (
                  <SelectItem key={c} value={c} className="text-xs">
                    {c}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex flex-col gap-1.5">
              <Label className="text-xs font-semibold">Frequency</Label>
              <Select value={frequency} onValueChange={setFrequency}>
                <SelectTrigger className="h-9 w-full text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {reportFormOptions.frequencies.map((f) => (
                    <SelectItem key={f} value={f} className="text-xs">
                      {f}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex flex-col gap-1.5">
              <Label className="text-xs font-semibold">Time</Label>
              <Select value={time} onValueChange={setTime}>
                <SelectTrigger className="h-9 w-full text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {reportFormOptions.times.map((t) => (
                    <SelectItem key={t} value={t} className="text-xs">
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label className="text-xs font-semibold">Delivery</Label>
            <Select value="app" onValueChange={() => {}}>
              <SelectTrigger className="h-9 w-full text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="app" className="text-xs">
                  Available in RivalTracking
                </SelectItem>
                <SelectItem value="email" disabled className="text-xs">
                  Email — coming soon
                </SelectItem>
                <SelectItem value="slack" disabled className="text-xs">
                  Slack — coming soon
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="h-9 rounded-lg text-xs font-semibold"
          >
            Cancel
          </Button>
          <Button onClick={save} className="h-9 rounded-lg text-xs font-bold">
            {schedule ? "Save changes" : "Schedule report"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
