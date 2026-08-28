import { X } from "lucide-react"

import type { AIQueryContext } from "@/lib/ask-ai-data"
import { useWorkspace } from "@/lib/workspace-store"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export type AskAIContext = AIQueryContext

const periods = ["Today", "Last 7 days", "Last 30 days", "Custom"]
const categories = ["Outdoor Toys", "Educational Toys", "Construction Toys", "Baby Toys", "Plush Toys", "Personalised Toys"]

export function AIContextBar({
  context,
  onChange,
}: {
  context: AskAIContext
  onChange: (context: AskAIContext) => void
}) {
  const { competitors } = useWorkspace()

  const chips = (
    [
      ["competitor", context.competitor],
      ["period", context.period],
      ["category", context.category],
      ["product", context.product],
      ["scope", context.scope === "all-competitors" ? "All competitors" : undefined],
    ] as const
  ).filter(([, v]) => v)

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="text-[11px] font-semibold text-muted-foreground">
        Context:
      </span>
      {chips.length === 0 && (
        <span className="text-[11px] text-muted-foreground">
          All monitored data
        </span>
      )}
      {chips.map(([key, value]) => (
        <Badge
          key={key}
          variant="outline"
          className="gap-1 rounded-full border-info/25 bg-info/10 px-2 py-0.5 text-[11px] font-bold text-info"
        >
          {value}
          <button
            onClick={() => onChange({ ...context, [key]: undefined })}
            aria-label={`Remove ${key} context`}
            className="ml-0.5 opacity-70 hover:opacity-100"
          >
            <X className="size-3" />
          </button>
        </Badge>
      ))}
      <span className="ml-auto flex items-center gap-1.5">
        <Select
          value={context.competitor ?? ""}
          onValueChange={(v) => onChange({ ...context, competitor: v, candidate: undefined })}
        >
          <SelectTrigger size="sm" className="h-7 text-[10px] font-semibold text-muted-foreground">
            <SelectValue placeholder="Competitor" />
          </SelectTrigger>
          <SelectContent>
            {competitors.map((c) => (
              <SelectItem key={c.slug} value={c.name} className="text-xs">{c.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={context.period ?? ""}
          onValueChange={(v) => onChange({ ...context, period: v })}
        >
          <SelectTrigger size="sm" className="h-7 text-[10px] font-semibold text-muted-foreground">
            <SelectValue placeholder="Date" />
          </SelectTrigger>
          <SelectContent>
            {periods.map((p) => (
              <SelectItem key={p} value={p} className="text-xs">{p}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={context.category ?? ""}
          onValueChange={(v) => onChange({ ...context, category: v })}
        >
          <SelectTrigger size="sm" className="h-7 text-[10px] font-semibold text-muted-foreground">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            {categories.map((c) => (
              <SelectItem key={c} value={c} className="text-xs">{c}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </span>
    </div>
  )
}
