import { type LucideIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { Card } from "@/components/ui/card"

export type KpiTone = "info" | "success" | "danger" | "warning" | "purple"

const toneClasses: Record<KpiTone, string> = {
  info: "bg-info/10 text-info",
  success: "bg-success/10 text-success",
  danger: "bg-destructive/10 text-destructive",
  warning: "bg-warning/10 text-warning",
  purple: "bg-purple/10 text-purple",
}

export function KpiCard({
  icon: Icon,
  tone,
  value,
  label,
  onClick,
}: {
  icon: LucideIcon
  tone: KpiTone
  value: string
  label: string
  onClick?: () => void
}) {
  return (
    <Card
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={onClick ? `${label}: ${value}` : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault()
                onClick()
              }
            }
          : undefined
      }
      className={cn(
        "gap-0 rounded-xl p-4 shadow-sm transition-shadow hover:shadow-md",
        onClick && "cursor-pointer"
      )}
    >
      <div
        className={cn(
          "mb-3 flex size-9 items-center justify-center rounded-full",
          toneClasses[tone]
        )}
      >
        <Icon className="size-4.5" />
      </div>
      <span className="block text-[23px] font-bold tracking-tight">{value}</span>
      <span className="mt-0.5 block text-[11px] font-semibold text-muted-foreground">
        {label}
      </span>
    </Card>
  )
}
