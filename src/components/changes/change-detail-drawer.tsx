import { useNavigate } from "react-router-dom"
import { ArrowRight, Clock3, ExternalLink, Sparkles } from "lucide-react"

import { type ChangeEvent, type SnapshotFields } from "@/lib/changes-data"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { ChangeBadge } from "@/components/shared/change-badge"
import { ChangeValue } from "@/components/shared/change-value"
import { ImpactBadge } from "@/components/shared/impact-badge"

const snapshotFields: { key: keyof SnapshotFields; label: string }[] = [
  { key: "price", label: "Price" },
  { key: "stock", label: "Stock" },
  { key: "promotion", label: "Promotion" },
]

function SnapshotPanel({
  title,
  snapshot,
  changedField,
  highlightClass,
}: {
  title: string
  snapshot: SnapshotFields
  changedField: keyof SnapshotFields
  highlightClass: string
}) {
  return (
    <div className="min-w-0 flex-1 rounded-xl border p-3">
      <p className="mb-2 text-[11px] font-bold text-muted-foreground">{title}</p>
      <div className="flex flex-col gap-1">
        {snapshotFields.map(({ key, label }) => (
          <div
            key={key}
            className={cn(
              "flex items-center justify-between gap-2 rounded-md px-1.5 py-1 text-xs",
              key === changedField && highlightClass
            )}
          >
            <span className="text-muted-foreground">{label}</span>
            <span
              className={cn(
                "font-medium",
                key === changedField ? "text-foreground" : "text-foreground/70"
              )}
            >
              {snapshot[key]}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function ChangeDetailDrawer({
  event,
  onClose,
}: {
  event: ChangeEvent | null
  onClose: () => void
}) {
  const navigate = useNavigate()

  return (
    <Sheet open={!!event} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full gap-0 overflow-y-auto sm:max-w-lg">
        <SheetHeader className="pb-3">
          <SheetTitle className="text-base font-bold">
            {event?.product.name}
          </SheetTitle>
          <SheetDescription className="flex flex-wrap items-center gap-2 text-xs">
            {event && (
              <>
                <ChangeBadge kind={event.kind} label={event.label} />
                <ImpactBadge impact={event.impact} />
              </>
            )}
          </SheetDescription>
        </SheetHeader>

        {event && (
          <div className="flex flex-col gap-4 px-4 pb-6">
            <div className="rounded-xl border p-3.5">
              <ChangeValue
                previous={event.previous}
                current={event.current}
                secondary={
                  [event.difference, event.secondary]
                    .filter(Boolean)
                    .join(" · ") || undefined
                }
                secondaryTone={event.secondaryTone ?? "muted"}
              />
            </div>

            <div className="grid grid-cols-2 gap-x-3 gap-y-2.5 text-xs">
              {[
                ["Competitor", event.competitor],
                ["Category", event.category],
                ["Detected", event.detectedAt],
                ["First seen at new value", event.firstSeenAt],
                ["Last confirmed", event.lastConfirmedAt],
              ].map(([label, value]) => (
                <div key={label}>
                  <span className="block text-[11px] text-muted-foreground">
                    {label}
                  </span>
                  <span className="mt-0.5 block font-medium">{value}</span>
                </div>
              ))}
            </div>

            <div>
              <p className="mb-2 text-xs font-bold">Change Evidence</p>
              <div className="flex flex-col gap-2.5 sm:flex-row">
                <SnapshotPanel
                  title="Previous snapshot"
                  snapshot={event.evidence.previous}
                  changedField={event.evidence.changedField}
                  highlightClass="bg-warning/10"
                />
                <SnapshotPanel
                  title="Current snapshot"
                  snapshot={event.evidence.current}
                  changedField={event.evidence.changedField}
                  highlightClass="bg-success/10"
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={!event.sourceUrl}
                onClick={() =>
                  event.sourceUrl &&
                  window.open(event.sourceUrl, "_blank", "noopener,noreferrer")
                }
                className="h-8 rounded-lg text-[11px] font-bold"
              >
                <ExternalLink className="size-3.5" /> View source product
              </Button>
              <span className="flex items-center gap-1 text-[11px] text-muted-foreground">
                <Clock3 className="size-3" /> Last successfully scanned:{" "}
                {event.lastScanned}
              </span>
            </div>

            <Button
              variant="ghost"
              onClick={() => {
                onClose()
                navigate(`/products/${event.product.slug}`)
              }}
              className="h-9 w-fit rounded-lg px-2 text-xs font-bold text-primary"
            >
              View full product history <ArrowRight className="size-3.5" />
            </Button>

            <div className="bg-ai-subtle flex items-start gap-2.5 rounded-xl border border-purple/20 p-3.5">
              <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-purple/10 text-purple">
                <Sparkles className="size-3.5" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold">Why this may matter</p>
                <p className="mt-1 text-[11px] leading-relaxed text-foreground/70">
                  {event.aiNote}
                </p>
                <Button
                  size="sm"
                  onClick={() => {
                    onClose()
                    navigate("/ask-ai", {
                      state: {
                        context: {
                          competitor: event.competitor,
                          product: event.product.name,
                        },
                        prompt: "Explain this change",
                      },
                    })
                  }}
                  className="mt-2.5 h-7 rounded-lg px-2.5 text-[11px] font-bold"
                >
                  Ask AI
                </Button>
              </div>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
