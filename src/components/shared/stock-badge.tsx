import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

export function StockBadge({ inStock }: { inStock: boolean }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "gap-1.5 rounded-full px-2 py-1 text-[11px] font-bold",
        inStock
          ? "border-success/30 bg-success/10 text-success"
          : "border-destructive/30 bg-destructive/10 text-destructive"
      )}
    >
      <i
        className={cn(
          "size-1.5 rounded-full",
          inStock ? "bg-success" : "bg-destructive"
        )}
      />
      {inStock ? "In stock" : "Out of stock"}
    </Badge>
  )
}
