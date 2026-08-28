import { type LucideIcon } from "lucide-react"

import { cn } from "@/lib/utils"

export type ProductTone = "info" | "purple" | "warning" | "rose" | "teal"

const toneClasses: Record<ProductTone, string> = {
  info: "bg-info/10 text-info",
  purple: "bg-purple/10 text-purple",
  warning: "bg-warning/10 text-warning",
  rose: "bg-rose/10 text-rose",
  teal: "bg-teal/10 text-teal",
}

export function ProductIdentity({
  icon: Icon,
  tone,
  name,
  sku,
  onClick,
}: {
  icon: LucideIcon
  tone: ProductTone
  name: string
  sku: string
  onClick?: () => void
}) {
  return (
    <div className="flex items-center gap-2.5">
      <span
        className={cn(
          "flex size-8.5 shrink-0 items-center justify-center rounded-lg",
          toneClasses[tone]
        )}
      >
        <Icon className="size-4" />
      </span>
      <span className="min-w-0">
        <span
          role={onClick ? "button" : undefined}
          onClick={onClick}
          className={cn(
            "block truncate text-sm font-medium text-foreground",
            onClick && "hover:text-primary hover:underline"
          )}
        >
          {name}
        </span>
        <span className="mt-0.5 block text-[11px] text-muted-foreground">
          {sku}
        </span>
      </span>
    </div>
  )
}
