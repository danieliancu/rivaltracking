import { useEffect, useRef, useState } from "react"
import { Check, CheckCircle2, Loader2 } from "lucide-react"
import { toast } from "sonner"

import {
  generationStages,
  reportFormOptions,
  reportTypes,
  type GeneratedReport,
} from "@/lib/reports-data"
import { useWorkspace } from "@/lib/workspace-store"
import { cn } from "@/lib/utils"
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
import { Switch } from "@/components/ui/switch"

type Phase = "form" | "generating" | "done"

function Field({
  step,
  label,
  children,
}: {
  step?: string
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label className="text-xs font-semibold">
        {step && <span className="mr-1 text-muted-foreground">{step}.</span>}
        {label}
      </Label>
      {children}
    </div>
  )
}

export type ReportPrefill = {
  typeId?: string
  competitors?: string
  dateRange?: string
  category?: string
  changeType?: string
  aiAnalysis?: boolean
}

export function CreateReportDialog({
  open,
  initialTypeId,
  prefill = null,
  onOpenChange,
  onView,
}: {
  open: boolean
  initialTypeId: string | null
  /* Full configuration prefill (used by Duplicate). */
  prefill?: ReportPrefill | null
  onOpenChange: (open: boolean) => void
  onView: (reportId: string) => void
}) {
  const { createReport } = useWorkspace()
  const [phase, setPhase] = useState<Phase>("form")
  const [typeId, setTypeId] = useState(reportTypes[0].id)
  const [competitors, setCompetitors] = useState(reportFormOptions.competitors[0])
  const [dateRange, setDateRange] = useState("Last 7 days")
  const [category, setCategory] = useState(reportFormOptions.categories[0])
  const [changeType, setChangeType] = useState(reportFormOptions.changeTypes[0])
  const [aiAnalysis, setAiAnalysis] = useState(true)
  const [stage, setStage] = useState(0)
  const [generated, setGenerated] = useState<GeneratedReport | null>(null)
  const timers = useRef<number[]>([])

  useEffect(() => {
    if (initialTypeId) setTypeId(initialTypeId)
  }, [initialTypeId])

  useEffect(() => {
    if (!prefill) return
    if (prefill.typeId) setTypeId(prefill.typeId)
    if (prefill.competitors) setCompetitors(prefill.competitors)
    if (prefill.dateRange) setDateRange(prefill.dateRange)
    if (prefill.category) setCategory(prefill.category)
    if (prefill.changeType) setChangeType(prefill.changeType)
    if (prefill.aiAnalysis !== undefined) setAiAnalysis(prefill.aiAnalysis)
  }, [prefill])

  useEffect(() => () => timers.current.forEach(window.clearTimeout), [])

  const reset = () => {
    timers.current.forEach(window.clearTimeout)
    timers.current = []
    setPhase("form")
    setStage(0)
    setGenerated(null)
  }

  const generate = () => {
    setPhase("generating")
    const type = reportTypes.find((t) => t.id === typeId) ?? reportTypes[0]
    generationStages.forEach((_, i) => {
      timers.current.push(
        window.setTimeout(() => {
          setStage(i + 1)
          if (i === generationStages.length - 1) {
            void createReport({
              typeId: type.id,
              type: type.title,
              competitors:
                competitors === reportFormOptions.competitors[0]
                  ? "All"
                  : competitors,
              period: dateRange,
              category:
                category !== reportFormOptions.categories[0]
                  ? category
                  : undefined,
              changeType:
                changeType !== reportFormOptions.changeTypes[0]
                  ? changeType
                  : undefined,
              aiAnalysis,
            }).then((report) => {
              setGenerated(report)
              setPhase("done")
              toast.success("Report generated", { description: report.name })
            })
          }
        }, 650 * (i + 1))
      )
    })
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        onOpenChange(o)
        if (!o) reset()
      }}
    >
      <DialogContent className="sm:max-w-md">
        {phase !== "done" && (
          <DialogHeader>
            <DialogTitle className="text-base font-bold">
              Create report
            </DialogTitle>
            <DialogDescription className="text-xs">
              Facts are calculated from your verified competitor data; AI adds
              interpretation on top.
            </DialogDescription>
          </DialogHeader>
        )}

        {phase === "form" && (
          <>
            <div className="flex flex-col gap-3.5">
              <Field step="1" label="Report type">
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
              </Field>
              <Field step="2" label="Competitors">
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
              </Field>
              <Field step="3" label="Date range">
                <Select value={dateRange} onValueChange={setDateRange}>
                  <SelectTrigger className="h-9 w-full text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {reportFormOptions.dateRanges.map((d) => (
                      <SelectItem key={d} value={d} className="text-xs">
                        {d}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-[11px] text-muted-foreground">
                  Historical data available since{" "}
                  {reportFormOptions.historicalSince}.
                  {dateRange === "Custom" &&
                    " Only data collected since monitoring started will be included."}
                </p>
              </Field>
              <Field step="4" label="Optional filters">
                <div className="grid grid-cols-2 gap-2">
                  <Select value={category} onValueChange={setCategory}>
                    <SelectTrigger className="h-9 w-full text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {reportFormOptions.categories.map((c) => (
                        <SelectItem key={c} value={c} className="text-xs">
                          {c}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select value={changeType} onValueChange={setChangeType}>
                    <SelectTrigger className="h-9 w-full text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {reportFormOptions.changeTypes.map((c) => (
                        <SelectItem key={c} value={c} className="text-xs">
                          {c}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </Field>
              <div className="flex items-start justify-between gap-3 rounded-xl border p-3">
                <div>
                  <Label
                    htmlFor="ai-analysis"
                    className="text-xs font-semibold"
                  >
                    <span className="mr-1 text-muted-foreground">5.</span>
                    AI analysis
                  </Label>
                  <p className="mt-1 text-[11px] leading-relaxed text-muted-foreground">
                    AI will interpret the verified analytics and highlight
                    important patterns, risks and opportunities.
                  </p>
                </div>
                <Switch
                  id="ai-analysis"
                  checked={aiAnalysis}
                  onCheckedChange={setAiAnalysis}
                />
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
              <Button
                onClick={generate}
                className="h-9 rounded-lg text-xs font-bold"
              >
                Generate report
              </Button>
            </DialogFooter>
          </>
        )}

        {phase === "generating" && (
          <div className="flex flex-col gap-2.5 py-1">
            <p className="text-xs font-bold">Preparing report</p>
            {generationStages.map((label, i) => {
              const done = stage > i
              const active = stage === i
              return (
                <div
                  key={label}
                  className={cn(
                    "flex items-center gap-2.5 text-xs font-semibold",
                    done
                      ? "text-success"
                      : active
                        ? "text-foreground"
                        : "text-muted-foreground/50"
                  )}
                >
                  {done ? (
                    <Check className="size-4" />
                  ) : active ? (
                    <Loader2 className="size-4 animate-spin text-primary" />
                  ) : (
                    <i className="size-4 rounded-full border border-border" />
                  )}
                  {label}
                </div>
              )
            })}
          </div>
        )}

        {phase === "done" && (
          <div className="flex flex-col items-center gap-1 py-2 text-center">
            <CheckCircle2 className="mb-1 size-10 text-success" />
            <p className="text-sm font-bold">Report ready</p>
            <p className="text-xs text-muted-foreground">
              Your report has been generated from verified competitor data.
            </p>
            <Button
              onClick={() => {
                const id = generated?.id
                onOpenChange(false)
                reset()
                if (id) onView(id)
              }}
              className="mt-3 h-9 rounded-lg text-xs font-bold"
            >
              View report
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
