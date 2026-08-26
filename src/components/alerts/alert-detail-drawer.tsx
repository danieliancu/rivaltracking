import { useNavigate } from "react-router-dom"
import {
  Boxes,
  ExternalLink,
  GitCompareArrows,
  Package,
  Pencil,
  Sparkles,
} from "lucide-react"

import { type RecentAlert } from "@/lib/alerts-data"
import { slugForCompetitor } from "@/lib/entities"
import { useWorkspace } from "@/lib/workspace-store"
import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { ChangeBadge } from "@/components/shared/change-badge"
import { ImpactBadge } from "@/components/shared/impact-badge"

export function AlertDetailDrawer({
  alert,
  onClose,
  onEditRule,
}: {
  alert: RecentAlert | null
  onClose: () => void
  onEditRule: (ruleId: string) => void
}) {
  const navigate = useNavigate()
  const { products } = useWorkspace()
  const go = (to: string) => {
    onClose()
    navigate(to)
  }

  const sourceUrl = alert?.productSlug
    ? products.find((p) => p.slug === alert.productSlug)?.sourceUrl
    : undefined

  return (
    <Sheet open={!!alert} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full gap-0 overflow-y-auto sm:max-w-lg">
        <SheetHeader className="pb-3">
          <SheetTitle className="text-base font-bold">
            {alert?.ruleName}
          </SheetTitle>
          <SheetDescription className="flex flex-wrap items-center gap-2 text-xs">
            {alert && (
              <>
                <ChangeBadge kind={alert.kind} label={alert.event} />
                <ImpactBadge impact={alert.priority} />
              </>
            )}
          </SheetDescription>
        </SheetHeader>

        {alert && (
          <div className="flex flex-col gap-4 px-4 pb-6">
            <div className="grid grid-cols-2 gap-x-3 gap-y-2.5 text-xs">
              {[
                [
                  alert.isPattern ? "Pattern" : "Product",
                  alert.isPattern ? alert.patternLabel : alert.product,
                ],
                ["Competitor", alert.competitor],
                ["Detected", alert.detectedAt],
                ["Triggered rule", alert.rule.condition],
              ].map(([label, value]) => (
                <div key={label}>
                  <span className="block text-[11px] text-muted-foreground">
                    {label}
                  </span>
                  <span className="mt-0.5 block font-medium">{value}</span>
                </div>
              ))}
            </div>

            {alert.evidence && (
              <div>
                <p className="mb-2 text-xs font-bold">Evidence</p>
                <div className="grid grid-cols-2 gap-2 rounded-xl border p-3 sm:grid-cols-3">
                  {[
                    ["Previous", alert.evidence.previous],
                    ["Current", alert.evidence.current],
                    ["Difference", alert.evidence.difference],
                    ["Change", alert.evidence.change],
                    ["Stock", alert.evidence.stock],
                    ["Category", alert.evidence.category],
                  ].map(([label, value]) => (
                    <div key={label}>
                      <span className="block text-[11px] text-muted-foreground">
                        {label}
                      </span>
                      <span className="mt-0.5 block text-xs font-medium">
                        {value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="rounded-xl border bg-background p-3.5">
              <p className="text-xs font-bold">Why you received this alert</p>
              <div className="mt-2 flex flex-col gap-1.5 text-[11px] text-muted-foreground">
                <p>
                  Your rule:{" "}
                  <span className="font-medium text-foreground">
                    {alert.rule.scope} · {alert.rule.condition}
                  </span>
                </p>
                <p>
                  Detected change:{" "}
                  <span className="font-medium text-foreground">
                    {alert.rule.detected}
                  </span>
                </p>
                <p className="font-medium text-success">Condition matched.</p>
              </div>
            </div>

            <div className="bg-ai-subtle flex items-start gap-2.5 rounded-xl border border-purple/20 p-3.5">
              <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-purple/10 text-purple">
                <Sparkles className="size-3.5" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold">Why this may matter</p>
                <p className="mt-1 text-[11px] leading-relaxed text-foreground/70">
                  {alert.aiNote}
                </p>
                <Button
                  size="sm"
                  onClick={() => {
                    onClose()
                    navigate("/ask-ai", {
                      state: {
                        context: {
                          competitor: alert.competitor,
                          product: alert.product,
                        },
                        prompt: "Explain this change",
                      },
                    })
                  }}
                  className="mt-2.5 h-7 rounded-lg px-2.5 text-[11px] font-bold"
                >
                  Ask AI about this
                </Button>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {!alert.isPattern && alert.productSlug && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => go(`/products/${alert.productSlug}`)}
                  className="h-8 rounded-lg text-[11px] font-bold"
                >
                  <Package className="size-3.5" /> View product
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  go(
                    alert.isPattern
                      ? "/changes"
                      : alert.productSlug
                        ? `/changes?product=${alert.productSlug}`
                        : "/changes"
                  )
                }
                className="h-8 rounded-lg text-[11px] font-bold"
              >
                <GitCompareArrows className="size-3.5" />{" "}
                {alert.isPattern ? "View pattern" : "View change"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  go(`/competitors/${slugForCompetitor(alert.competitor)}`)
                }
                className="h-8 rounded-lg text-[11px] font-bold"
              >
                <Boxes className="size-3.5" /> View competitor
              </Button>
              {sourceUrl && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    window.open(sourceUrl, "_blank", "noopener,noreferrer")
                  }
                  className="h-8 rounded-lg text-[11px] font-bold"
                >
                  <ExternalLink className="size-3.5" /> Open source
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  onClose()
                  onEditRule(alert.ruleId)
                }}
                className="h-8 rounded-lg text-[11px] font-bold"
              >
                <Pencil className="size-3.5" /> Edit alert rule
              </Button>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
