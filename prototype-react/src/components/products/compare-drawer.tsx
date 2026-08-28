import { GitCompareArrows, Sparkles } from "lucide-react"

import { type ProductRow } from "@/lib/products-data"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { StockBadge } from "@/components/shared/stock-badge"

export function CompareDrawer({
  product,
  onClose,
}: {
  product: ProductRow | null
  onClose: () => void
}) {
  const matched = product?.matched
  const lowestPrice = matched
    ? Math.min(...matched.listings.map((l) => l.price))
    : 0

  return (
    <Sheet open={!!product} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full gap-0 overflow-y-auto sm:max-w-xl">
        <SheetHeader className="pb-2">
          <SheetTitle className="text-base font-bold">
            {product?.name}
          </SheetTitle>
          <SheetDescription className="flex flex-wrap items-center gap-2 text-xs">
            Matched across {matched?.count} competitors
            <Badge
              variant="outline"
              className="gap-1 rounded-full border-info/25 bg-info/10 px-2 py-0.5 text-[11px] font-bold text-info"
            >
              <GitCompareArrows className="size-3" />
              Matched · {matched?.confidence}% confidence
            </Badge>
          </SheetDescription>
        </SheetHeader>

        <div className="px-4">
          <div className="overflow-x-auto rounded-xl border">
            <Table className="min-w-[480px]">
              <TableHeader>
                <TableRow>
                  <TableHead className="px-3.5 text-[10px] font-bold">Competitor</TableHead>
                  <TableHead className="px-3.5 text-[10px] font-bold">Price</TableHead>
                  <TableHead className="px-3.5 text-[10px] font-bold">Stock</TableHead>
                  <TableHead className="px-3.5 text-[10px] font-bold">Promotion</TableHead>
                  <TableHead className="px-3.5 text-[10px] font-bold">Last Scan</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {matched?.listings.map((l) => {
                  const isLowest = l.price === lowestPrice
                  return (
                    <TableRow
                      key={l.competitor}
                      className={cn(
                        "text-[11px] text-muted-foreground",
                        isLowest && "bg-success/5"
                      )}
                    >
                      <TableCell className="px-3.5 py-2.5">
                        <span className="block text-sm font-medium text-foreground">
                          {l.competitor}
                        </span>
                        {isLowest && (
                          <Badge
                            variant="outline"
                            className="mt-1 rounded-full border-success/25 bg-success/10 px-2 py-0.5 text-[11px] font-bold text-success"
                          >
                            Lowest price
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="px-3.5 font-medium text-foreground">
                        £{l.price.toFixed(2)}
                      </TableCell>
                      <TableCell className="px-3.5">
                        <StockBadge inStock={l.inStock} />
                      </TableCell>
                      <TableCell className="px-3.5">
                        {l.promotion ?? "—"}
                      </TableCell>
                      <TableCell className="px-3.5">{l.lastScan}</TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>

          {matched?.listings.some((l) => l.price === lowestPrice && !l.inStock) && (
            <p className="mt-2 text-[10px] text-muted-foreground">
              The lowest detected price is currently out of stock.
            </p>
          )}

          <div className="bg-ai-subtle mt-4 flex items-start gap-2.5 rounded-xl border border-purple/20 p-3.5">
            <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-purple/10 text-purple">
              <Sparkles className="size-3.5" />
            </span>
            <p className="text-[11px] leading-relaxed text-foreground/70">
              {matched?.insight}
            </p>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
