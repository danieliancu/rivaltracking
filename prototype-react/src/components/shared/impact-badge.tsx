import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

export type ImpactLevel = "high" | "medium" | "low"

/* Impact is computed by backend rules (Python); the UI only displays it. */
const impactMeta: Record<ImpactLevel, { label: string; classes: string }> = {
  high: {
    label: "High",
    classes: "border-warning/30 bg-warning/10 text-warning",
  },
  medium: {
    label: "Medium",
    classes: "border-info/25 bg-info/10 text-info",
  },
  low: {
    label: "Low",
    classes: "border-border bg-muted text-muted-foreground",
  },
}

export function ImpactBadge({ impact }: { impact: ImpactLevel }) {
  const meta = impactMeta[impact]
  return (
    <Badge
      variant="outline"
      className={cn(
        "rounded-full px-2 py-1 text-[11px] font-bold",
        meta.classes
      )}
    >
      {meta.label}
    </Badge>
  )
}
