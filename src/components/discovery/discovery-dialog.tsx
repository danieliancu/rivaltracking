import { useEffect, useRef, useState } from "react"
import { Check, Loader2 } from "lucide-react"

import { discoveryModes, discoveryStages } from "@/lib/discovery-data"
import type { DiscoveryMode } from "@/services/discovery"
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
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const inputLabels: Partial<Record<DiscoveryMode, { label: string; placeholder: string }>> = {
  website: { label: "Website", placeholder: "https://competitor.com" },
  category: { label: "Category", placeholder: "e.g. Outdoor Toys" },
  brand: { label: "Brand", placeholder: "e.g. LEGO" },
  market: { label: "Market", placeholder: "e.g. UK Toys" },
}

export function DiscoveryDialog({
  open,
  onOpenChange,
  onRun,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onRun: (mode: DiscoveryMode, input: string) => Promise<void>
}) {
  const [mode, setMode] = useState<DiscoveryMode>("existing")
  const [input, setInput] = useState("")
  const [running, setRunning] = useState(false)
  const [stage, setStage] = useState(0)
  const timers = useRef<number[]>([])

  useEffect(() => () => timers.current.forEach(window.clearTimeout), [])

  const reset = () => {
    timers.current.forEach(window.clearTimeout)
    timers.current = []
    setRunning(false)
    setStage(0)
    setInput("")
  }

  const start = () => {
    setRunning(true)
    setStage(0)
    discoveryStages.forEach((_, i) => {
      timers.current.push(
        window.setTimeout(() => {
          setStage(i + 1)
          if (i === discoveryStages.length - 1) {
            void onRun(mode, input).finally(() => {
              onOpenChange(false)
              reset()
            })
          }
        }, 700 * (i + 1))
      )
    })
  }

  const inputMeta = inputLabels[mode]

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        onOpenChange(o)
        if (!o) reset()
      }}
    >
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-base font-bold">
            Discover competitors
          </DialogTitle>
          <DialogDescription className="text-xs">
            The Discovery Engine finds companies with overlapping catalogues and
            comparable positioning.
          </DialogDescription>
        </DialogHeader>

        {!running ? (
          <>
            <div className="flex flex-col gap-3">
              <div className="flex flex-col gap-2">
                <Label className="text-xs font-semibold">Discovery mode</Label>
                <Select value={mode} onValueChange={(v) => setMode(v as DiscoveryMode)}>
                  <SelectTrigger className="h-9 w-full text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {discoveryModes.map((m) => (
                      <SelectItem key={m.value} value={m.value} className="text-xs">
                        {m.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              {inputMeta && (
                <div className="flex flex-col gap-2">
                  <Label htmlFor="discovery-input" className="text-xs font-semibold">
                    {inputMeta.label}
                  </Label>
                  <Input
                    id="discovery-input"
                    placeholder={inputMeta.placeholder}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="h-9 text-xs"
                  />
                </div>
              )}
              <p className="text-[11px] leading-relaxed text-muted-foreground">
                Candidates come from the Discovery Engine's catalogue comparison —
                no historical data exists until a company is monitored.
              </p>
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
                onClick={start}
                disabled={!!inputMeta && input.trim() === ""}
                className="h-9 rounded-lg text-xs font-bold"
              >
                Start discovery
              </Button>
            </DialogFooter>
          </>
        ) : (
          <div className="flex flex-col gap-2.5 py-1">
            {discoveryStages.map((label, i) => {
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
      </DialogContent>
    </Dialog>
  )
}
