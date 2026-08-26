import { type ReportStatus } from "@/lib/reports-data"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

const statusMeta: Record<
  ReportStatus,
  { label: string; classes: string; dot: string; animate?: boolean }
> = {
  generating: {
    label: "Generating",
    classes: "border-info/25 bg-info/10 text-info",
    dot: "bg-info",
    animate: true,
  },
  ready: {
    label: "Ready",
    classes: "border-success/25 bg-success/10 text-success",
    dot: "bg-success",
  },
  attention: {
    label: "Attention",
    classes: "border-warning/25 bg-warning/10 text-warning",
    dot: "bg-warning",
  },
  failed: {
    label: "Failed",
    classes: "border-destructive/25 bg-destructive/10 text-destructive",
    dot: "bg-destructive",
  },
}

export function ReportStatusBadge({ status }: { status: ReportStatus }) {
  const meta = statusMeta[status]
  return (
    <Badge
      variant="outline"
      className={cn(
        "gap-1.5 rounded-full px-2 py-1 text-[11px] font-bold",
        meta.classes
      )}
    >
      <i
        className={cn(
          "size-1.5 rounded-full",
          meta.dot,
          meta.animate && "animate-pulse"
        )}
      />
      {meta.label}
    </Badge>
  )
}
