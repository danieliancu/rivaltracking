import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

export type MonitoringStatus =
  | "healthy"
  | "scanning"
  | "attention"
  | "paused"
  | "initialising"

const statusMeta: Record<
  MonitoringStatus,
  { label: string; classes: string; dot: string; animate?: boolean }
> = {
  healthy: {
    label: "Healthy",
    classes: "border-success/25 bg-success/10 text-success",
    dot: "bg-success",
  },
  scanning: {
    label: "Scanning",
    classes: "border-info/25 bg-info/10 text-info",
    dot: "bg-info",
    animate: true,
  },
  attention: {
    label: "Attention",
    classes: "border-warning/25 bg-warning/10 text-warning",
    dot: "bg-warning",
  },
  paused: {
    label: "Paused",
    classes: "border-border bg-muted text-muted-foreground",
    dot: "bg-muted-foreground",
  },
  initialising: {
    label: "Initialising",
    classes: "border-purple/25 bg-purple/10 text-purple",
    dot: "bg-purple",
    animate: true,
  },
}

export function StatusBadge({ status }: { status: MonitoringStatus }) {
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
