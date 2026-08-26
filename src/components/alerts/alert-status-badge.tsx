import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

export function AlertRuleStatusBadge({ active }: { active: boolean }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "gap-1.5 rounded-full px-2 py-1 text-[11px] font-bold",
        active
          ? "border-success/25 bg-success/10 text-success"
          : "border-border bg-muted text-muted-foreground"
      )}
    >
      <i
        className={cn(
          "size-1.5 rounded-full",
          active ? "bg-success" : "bg-muted-foreground"
        )}
      />
      {active ? "Active" : "Paused"}
    </Badge>
  )
}

export function NotificationStatusBadge({ status }: { status: "new" | "viewed" }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "rounded-full px-2 py-1 text-[11px] font-bold",
        status === "new"
          ? "border-info/25 bg-info/10 text-info"
          : "border-border bg-muted text-muted-foreground"
      )}
    >
      {status === "new" ? "New" : "Viewed"}
    </Badge>
  )
}
