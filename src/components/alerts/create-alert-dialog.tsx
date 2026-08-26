import { useEffect, useState } from "react"

import {
  alertFormOptions,
  alertTriggerGroups,
  type AlertRule,
  type AlertTypeGroup,
} from "@/lib/alerts-data"
import type { ImpactLevel } from "@/components/shared/impact-badge"
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

export type AlertPrefill = {
  competitor?: string
  triggerId?: string
  category?: string
  product?: string
}

/* Best-effort mapping of an existing rule back onto the form (edit mode).
   The mock rule model stores a rendered condition string, so numeric
   thresholds are recovered by parsing. */
const triggerByTypeGroup: Record<AlertTypeGroup, string> = {
  price: "price-decrease",
  stock: "stock-out",
  products: "product-new",
  promotions: "promo-start",
  patterns: "related-changes",
}

function Section({
  step,
  label,
  children,
}: {
  step: string
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label className="text-xs font-semibold">
        <span className="mr-1 text-muted-foreground">{step}.</span>
        {label}
      </Label>
      {children}
    </div>
  )
}

export function CreateAlertDialog({
  open,
  prefill,
  editRule = null,
  onOpenChange,
  onCreated,
}: {
  open: boolean
  prefill: AlertPrefill | null
  /* When set, the dialog edits this rule instead of creating a new one. */
  editRule?: AlertRule | null
  onOpenChange: (open: boolean) => void
  onCreated: (rule: AlertRule) => void
}) {
  const [triggerId, setTriggerId] = useState("price-decrease")
  const [operator, setOperator] = useState("more than")
  const [threshold, setThreshold] = useState("10")
  const [patternCount, setPatternCount] = useState("20")
  const [patternHours, setPatternHours] = useState("6")
  const [competitor, setCompetitor] = useState(alertFormOptions.competitors[0])
  const [category, setCategory] = useState(alertFormOptions.categories[0])
  const [brand, setBrand] = useState("")
  const [product, setProduct] = useState("")
  const [priority, setPriority] = useState<ImpactLevel>("medium")
  const [frequency, setFrequency] = useState("Immediate")

  /* (Re)initialise the form each time the dialog opens so values from a
     previous session do not leak into a fresh create. */
  useEffect(() => {
    if (!open) return
    if (editRule) {
      const condition = editRule.condition.toLowerCase()
      setTriggerId(
        editRule.typeGroup === "price" && condition.includes("increase")
          ? "price-increase"
          : editRule.typeGroup === "stock" && condition.includes("back")
            ? "stock-back"
            : editRule.typeGroup === "products" && condition.includes("removed")
              ? "product-removed"
              : triggerByTypeGroup[editRule.typeGroup]
      )
      const pctMatch = editRule.condition.match(/(\d+)\s*%/)
      if (pctMatch) setThreshold(pctMatch[1])
      setOperator(condition.includes("less than") ? "less than" : "more than")
      setCompetitor(
        alertFormOptions.competitors.includes(editRule.competitors)
          ? editRule.competitors
          : alertFormOptions.competitors[0]
      )
      setCategory(editRule.category ?? alertFormOptions.categories[0])
      setPriority(editRule.priority ?? "low")
      setFrequency(editRule.frequency)
      setBrand("")
      setProduct("")
      return
    }
    setTriggerId(prefill?.triggerId ?? "price-decrease")
    setOperator("more than")
    setThreshold("10")
    setPatternCount("20")
    setPatternHours("6")
    setCompetitor(prefill?.competitor ?? alertFormOptions.competitors[0])
    setCategory(prefill?.category ?? alertFormOptions.categories[0])
    setBrand("")
    setProduct(prefill?.product ?? "")
    setPriority("medium")
    setFrequency("Immediate")
  }, [open, prefill, editRule])

  const trigger = alertTriggerGroups
    .flatMap((g) => g.options.map((o) => ({ ...o, typeGroup: g.typeGroup })))
    .find((o) => o.id === triggerId)
  const isPrice = trigger?.typeGroup === "price"
  const isPattern = triggerId === "related-changes"

  const condition = isPrice
    ? `${trigger?.label.replace(/s$/, "s")} by ${operator} ${threshold}%`
    : isPattern
      ? `${patternCount}+ related changes within ${patternHours} hours`
      : trigger?.label ?? ""

  const summary = [
    competitor,
    condition.toLowerCase(),
    category !== alertFormOptions.categories[0] ? `in ${category}` : null,
    brand && `brand: ${brand}`,
    product && `product: ${product}`,
  ]
    .filter(Boolean)
    .join(" · ")

  const create = () => {
    onCreated({
      id: editRule?.id ?? `rule-${triggerId}-${threshold}-${category}`,
      name: editRule
        ? editRule.name
        : product
          ? `${trigger?.label} — ${product}`
          : `${trigger?.label} — ${
              competitor === alertFormOptions.competitors[0]
                ? "All competitors"
                : competitor
            }`,
      typeGroup: (trigger?.typeGroup ?? "price") as AlertTypeGroup,
      condition,
      competitors: competitor,
      category:
        category !== alertFormOptions.categories[0] ? category : undefined,
      frequency,
      lastTriggered: editRule?.lastTriggered ?? "Never",
      active: editRule?.active ?? true,
      priority: priority !== "low" ? priority : undefined,
      patternBased: isPattern,
      createdAt: editRule?.createdAt ?? new Date().toISOString().slice(0, 10),
    })
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-base font-bold">
            {editRule ? "Edit alert rule" : "Create alert"}
          </DialogTitle>
          <DialogDescription className="text-xs">
            {editRule
              ? `Adjust what "${editRule.name}" watches for.`
              : "Choose what CompeteIQ should watch for."}
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          <Section step="1" label="What should trigger the alert?">
            <div className="flex flex-col gap-2.5">
              {alertTriggerGroups.map((g) => (
                <div key={g.group}>
                  <p className="mb-1.5 text-[11px] font-semibold text-muted-foreground">
                    {g.group}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {g.options.map((o) => (
                      <button
                        key={o.id}
                        onClick={() => setTriggerId(o.id)}
                        className={cn(
                          "rounded-full border px-2.5 py-1 text-[11px] font-semibold transition-colors",
                          triggerId === o.id
                            ? "border-primary bg-primary text-primary-foreground"
                            : "bg-card text-muted-foreground hover:border-primary/40"
                        )}
                      >
                        {o.label}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Section>

          {isPrice && (
            <Section step="2" label="Conditions">
              <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                Price changes by
                <Select value={operator} onValueChange={setOperator}>
                  <SelectTrigger size="sm" className="h-8 w-28 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {alertFormOptions.operators.map((o) => (
                      <SelectItem key={o} value={o} className="text-xs">
                        {o}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Input
                  value={threshold}
                  onChange={(e) => setThreshold(e.target.value.replace(/\D/g, ""))}
                  className="h-8 w-16 text-center text-xs"
                />
                % or more
              </div>
            </Section>
          )}

          {isPattern && (
            <Section step="2" label="Conditions">
              <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                More than
                <Input
                  value={patternCount}
                  onChange={(e) => setPatternCount(e.target.value.replace(/\D/g, ""))}
                  className="h-8 w-16 text-center text-xs"
                />
                related changes within
                <Input
                  value={patternHours}
                  onChange={(e) => setPatternHours(e.target.value.replace(/\D/g, ""))}
                  className="h-8 w-14 text-center text-xs"
                />
                hours
              </div>
            </Section>
          )}

          <Section step="3" label="Where should this apply?">
            <div className="grid grid-cols-2 gap-2">
              <Select value={competitor} onValueChange={setCompetitor}>
                <SelectTrigger className="h-9 w-full text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {alertFormOptions.competitors.map((c) => (
                    <SelectItem key={c} value={c} className="text-xs">
                      {c}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger className="h-9 w-full text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {alertFormOptions.categories.map((c) => (
                    <SelectItem key={c} value={c} className="text-xs">
                      {c}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input
                placeholder="Brand (optional)"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                className="h-9 text-xs"
              />
              <Input
                placeholder="Product (optional)"
                value={product}
                onChange={(e) => setProduct(e.target.value)}
                className="h-9 text-xs"
              />
            </div>
          </Section>

          <Section step="4" label="Priority">
            <div className="grid grid-cols-3 gap-2">
              {alertFormOptions.priorities.map((p) => (
                <button
                  key={p.value}
                  onClick={() => setPriority(p.value as ImpactLevel)}
                  className={cn(
                    "rounded-xl border p-2.5 text-left transition-colors",
                    priority === p.value
                      ? "border-primary bg-accent"
                      : "bg-card hover:border-primary/40"
                  )}
                >
                  <span className="block text-xs font-bold">{p.label}</span>
                  <span className="mt-0.5 block text-[11px] text-muted-foreground">
                    {p.hint}
                  </span>
                </button>
              ))}
            </div>
          </Section>

          <Section step="5" label="Notification frequency">
            <Select value={frequency} onValueChange={setFrequency}>
              <SelectTrigger className="h-9 w-full text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {alertFormOptions.frequencies.map((f) => (
                  <SelectItem key={f.value} value={f.value} className="text-xs">
                    {f.value} — {f.hint}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Section>

          <Section step="6" label="Delivery">
            <Select value="app" onValueChange={() => {}}>
              <SelectTrigger className="h-9 w-full text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="app" className="text-xs">
                  In CompeteIQ
                </SelectItem>
                <SelectItem value="email" disabled className="text-xs">
                  Email — coming later
                </SelectItem>
                <SelectItem value="slack" disabled className="text-xs">
                  Slack — coming later
                </SelectItem>
              </SelectContent>
            </Select>
          </Section>

          <div className="rounded-xl border bg-background p-3">
            <p className="text-[11px] font-bold text-muted-foreground">
              Alert me when:
            </p>
            <p className="mt-1 text-xs font-medium leading-relaxed">{summary}</p>
            <p className="mt-1 text-[11px] text-muted-foreground">
              Priority: {priority[0].toUpperCase() + priority.slice(1)} ·
              Delivery: {frequency}
            </p>
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
          <Button onClick={create} className="h-9 rounded-lg text-xs font-bold">
            {editRule ? "Save changes" : "Create alert"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
