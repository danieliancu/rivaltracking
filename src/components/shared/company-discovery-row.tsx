import { Check, Loader2, Plus, Store } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export type DiscoveryTone = "blue" | "purple" | "teal" | "orange"

const toneClasses: Record<DiscoveryTone, string> = {
  blue: "bg-info/10 text-info",
  purple: "bg-purple/10 text-purple",
  teal: "bg-teal/10 text-teal",
  orange: "bg-warning/10 text-warning",
}

export function CompanyDiscoveryRow({
  name,
  match,
  tone,
  monitoring,
  pending = false,
  onToggle,
}: {
  name: string
  match: number
  tone: DiscoveryTone
  monitoring: boolean
  pending?: boolean
  onToggle: () => void
}) {
  return (
    <div className="flex items-center gap-2.5 border-t px-5 py-3">
      <span
        className={cn(
          "flex size-8.5 shrink-0 items-center justify-center rounded-lg",
          toneClasses[tone]
        )}
      >
        <Store className="size-4" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-medium">{name}</span>
        <span className="mt-0.5 block text-[11px] text-muted-foreground">
          {match}% match
        </span>
      </span>
      <Button
        variant="outline"
        size="sm"
        onClick={onToggle}
        disabled={pending || monitoring}
        className={cn(
          "h-7 rounded-lg px-2.5 text-[11px] font-bold",
          monitoring &&
            "border-success/30 bg-success/10 text-success hover:bg-success/15 hover:text-success disabled:opacity-100"
        )}
      >
        {pending ? (
          <Loader2 className="size-3.5 animate-spin" />
        ) : monitoring ? (
          <Check className="size-3.5" />
        ) : (
          <Plus className="size-3.5" />
        )}
        {pending ? "Monitoring…" : monitoring ? "Monitoring" : "Monitor"}
      </Button>
    </div>
  )
}
