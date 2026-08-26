import { useEffect, useRef, useState } from "react"
import { Check, CheckCircle2, Loader2, Plus } from "lucide-react"
import { toast } from "sonner"

import { scanStages, type CompetitorRow } from "@/lib/competitors-data"
import { slugify } from "@/lib/entities"
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
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type Phase = "form" | "scanning" | "done"

function validateUrl(raw: string): { host: string } | { error: string } {
  const input = raw.trim()
  if (!input) return { error: "Enter the competitor's website address." }
  try {
    const url = new URL(/^https?:\/\//i.test(input) ? input : `https://${input}`)
    if (!url.hostname.includes(".")) {
      return { error: "Enter a valid website address, e.g. competitor.com." }
    }
    return { host: url.hostname.replace(/^www\./, "") }
  } catch {
    return { error: "Enter a valid website address, e.g. competitor.com." }
  }
}

export function AddCompetitorDialog({ onView }: { onView: (slug: string) => void }) {
  const { competitors, addCompetitor } = useWorkspace()
  const [open, setOpen] = useState(false)
  const [phase, setPhase] = useState<Phase>("form")
  const [url, setUrl] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [stage, setStage] = useState(0)
  const [added, setAdded] = useState<CompetitorRow | null>(null)
  const timers = useRef<number[]>([])

  useEffect(() => () => timers.current.forEach(window.clearTimeout), [])

  const reset = () => {
    timers.current.forEach(window.clearTimeout)
    timers.current = []
    setPhase("form")
    setStage(0)
    setUrl("")
    setError(null)
    setAdded(null)
  }

  const startMonitoring = () => {
    const result = validateUrl(url)
    if ("error" in result) {
      setError(result.error)
      return
    }
    if (competitors.some((c) => c.slug === slugify(result.host))) {
      setError("You are already monitoring this competitor.")
      return
    }
    setError(null)
    setPhase("scanning")
    scanStages.forEach((_, i) => {
      timers.current.push(
        window.setTimeout(() => {
          setStage(i + 1)
          if (i === scanStages.length - 1) {
            void addCompetitor(result.host).then((row) => {
              setAdded(row)
              setPhase("done")
              toast.success("Competitor added", {
                description: `Now monitoring ${row.name}.`,
              })
            })
          }
        }, 700 * (i + 1))
      )
    })
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        setOpen(o)
        if (!o) reset()
      }}
    >
      <Button
        onClick={() => setOpen(true)}
        className="h-9 rounded-lg text-xs font-bold shadow-md shadow-primary/25"
      >
        <Plus className="size-4" /> Add competitor
      </Button>

      <DialogContent className="sm:max-w-md">
        {phase !== "done" && (
          <DialogHeader>
            <DialogTitle className="text-base font-bold">
              Monitor a competitor
            </DialogTitle>
            <DialogDescription className="text-xs">
              Enter a competitor website and CompeteIQ will discover its
              catalogue automatically.
            </DialogDescription>
          </DialogHeader>
        )}

        {phase === "form" && (
          <>
            <div className="flex flex-col gap-2">
              <Label htmlFor="competitor-url" className="text-xs font-semibold">
                Competitor website
              </Label>
              <Input
                id="competitor-url"
                placeholder="https://competitor.com"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value)
                  if (error) setError(null)
                }}
                aria-invalid={!!error}
                className={cn("h-9 text-xs", error && "border-destructive")}
              />
              {error && (
                <p className="text-[11px] font-semibold text-destructive">{error}</p>
              )}
              <p className="text-[11px] leading-relaxed text-muted-foreground">
                CompeteIQ will detect products, categories, prices, stock and
                promotions from publicly accessible pages.
              </p>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setOpen(false)}
                className="h-9 rounded-lg text-xs font-semibold"
              >
                Cancel
              </Button>
              <Button
                onClick={startMonitoring}
                className="h-9 rounded-lg text-xs font-bold"
              >
                Start monitoring
              </Button>
            </DialogFooter>
          </>
        )}

        {phase === "scanning" && (
          <div className="flex flex-col gap-2.5 py-1">
            {scanStages.map((label, i) => {
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

        {phase === "done" && added && (
          <div className="flex flex-col items-center gap-1 py-2 text-center">
            <CheckCircle2 className="mb-1 size-10 text-success" />
            <p className="text-sm font-bold">{added.name} successfully added</p>
            <p className="text-xs text-muted-foreground">
              <strong className="text-foreground">
                {(added.products ?? 0).toLocaleString()}
              </strong>{" "}
              products discovered
            </p>
            <p className="text-xs text-muted-foreground">
              Initial snapshot created — changes appear after the next scan.
            </p>
            <Button
              onClick={() => {
                setOpen(false)
                const slug = added.slug
                reset()
                onView(slug)
              }}
              className="mt-3 h-9 rounded-lg text-xs font-bold"
            >
              View competitor
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
