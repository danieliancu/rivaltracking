import { useEffect, useState } from "react"
import { Loader2 } from "lucide-react"
import { toast } from "sonner"

import type { CompetitorRow } from "@/lib/competitors-data"
import type { CompetitorMonitoringConfig } from "@/services/competitors"
import { useWorkspace } from "@/lib/workspace-store"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Switch } from "@/components/ui/switch"

/* Configuration only: the values represent future Django/Celery scheduling.
   No timers run in the frontend. */
const frequencies = ["Every 24 hours", "Every 12 hours", "Every 6 hours"]

const trackingRows: { key: keyof Omit<CompetitorMonitoringConfig, "frequency">; label: string; hint: string }[] = [
  { key: "trackPrices", label: "Track prices", hint: "Detect price increases and decreases." },
  { key: "trackStock", label: "Track stock", hint: "Detect stock-outs and restocks." },
  { key: "trackProducts", label: "Track new/removed products", hint: "Detect catalogue changes." },
  { key: "trackPromotions", label: "Track promotions", hint: "Detect promotions starting and ending." },
]

export function MonitoringSettingsDrawer({
  competitor,
  onClose,
}: {
  competitor: CompetitorRow | null
  onClose: () => void
}) {
  const { getCompetitorConfig, saveCompetitorConfig } = useWorkspace()
  const [config, setConfig] = useState<CompetitorMonitoringConfig | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (competitor) setConfig(getCompetitorConfig(competitor.slug))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [competitor?.slug])

  const save = async () => {
    if (!competitor || !config || saving) return
    setSaving(true)
    try {
      await saveCompetitorConfig(competitor.slug, config)
      toast.success("Settings saved", {
        description: `Monitoring settings updated for ${competitor.name}.`,
      })
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <Sheet open={!!competitor} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full gap-0 overflow-y-auto sm:max-w-md">
        <SheetHeader className="pb-3">
          <SheetTitle className="text-base font-bold">
            Monitoring settings
          </SheetTitle>
          <SheetDescription className="text-xs">
            {competitor?.name} — configure how this competitor is scanned.
          </SheetDescription>
        </SheetHeader>

        {config && (
          <div className="flex flex-col gap-4 px-4 pb-6">
            <div className="flex flex-col gap-2">
              <Label className="text-xs font-semibold">Scan frequency</Label>
              <Select
                value={config.frequency}
                onValueChange={(v) => setConfig({ ...config, frequency: v })}
              >
                <SelectTrigger className="h-9 w-full text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {frequencies.map((f) => (
                    <SelectItem key={f} value={f} className="text-xs">
                      {f}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-[11px] text-muted-foreground">
                Scheduling is handled by the monitoring backend.
              </p>
            </div>

            <div className="flex flex-col gap-1 rounded-xl border p-3.5">
              {trackingRows.map(({ key, label, hint }) => (
                <div
                  key={key}
                  className="flex items-center justify-between gap-3 py-1.5"
                >
                  <span>
                    <span className="block text-xs font-semibold">{label}</span>
                    <span className="mt-0.5 block text-[11px] text-muted-foreground">
                      {hint}
                    </span>
                  </span>
                  <Switch
                    checked={config[key]}
                    onCheckedChange={(checked) =>
                      setConfig({ ...config, [key]: checked })
                    }
                    aria-label={label}
                  />
                </div>
              ))}
            </div>

            <Button
              onClick={save}
              disabled={saving}
              className="h-9 w-fit rounded-lg text-xs font-bold"
            >
              {saving && <Loader2 className="size-3.5 animate-spin" />}
              {saving ? "Saving…" : "Save settings"}
            </Button>
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
