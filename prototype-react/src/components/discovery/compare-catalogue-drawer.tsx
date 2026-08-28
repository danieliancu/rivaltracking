import { GitCompareArrows } from "lucide-react"

import type { DiscoveryCandidate } from "@/lib/discovery-data"
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

/* Catalogue profile of the monitored reference competitor. Comparison uses
   current catalogue data only — no historical trends exist for candidates. */
const toyworldProfile = {
  name: "ToyWorld.co.uk",
  products: 2438,
  priceBand: "£5 – £250",
  categories: "Outdoor Toys · Construction Toys · Educational Toys",
}

export function CompareCatalogueDrawer({
  candidate,
  onClose,
}: {
  candidate: DiscoveryCandidate | null
  onClose: () => void
}) {
  return (
    <Sheet open={!!candidate} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full gap-0 overflow-y-auto sm:max-w-xl">
        <SheetHeader className="pb-2">
          <SheetTitle className="text-base font-bold">
            {candidate?.name} vs {toyworldProfile.name}
          </SheetTitle>
          <SheetDescription className="flex flex-wrap items-center gap-2 text-xs">
            Catalogue profile comparison
            <Badge
              variant="outline"
              className="gap-1 rounded-full border-info/25 bg-info/10 px-2 py-0.5 text-[11px] font-bold text-info"
            >
              <GitCompareArrows className="size-3" />
              {candidate?.catalogueProfile.overlap}
            </Badge>
          </SheetDescription>
        </SheetHeader>

        {candidate && (
          <div className="px-4 pb-6">
            <div className="overflow-x-auto rounded-xl border">
              <Table className="min-w-[440px]">
                <TableHeader>
                  <TableRow>
                    <TableHead className="px-3.5 text-[10px] font-bold" />
                    <TableHead className="px-3.5 text-[10px] font-bold">
                      {candidate.name}
                    </TableHead>
                    <TableHead className="px-3.5 text-[10px] font-bold">
                      {toyworldProfile.name}
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[
                    [
                      "Products",
                      candidate.catalogueProfile.products.toLocaleString(),
                      toyworldProfile.products.toLocaleString(),
                    ],
                    [
                      "Price band",
                      candidate.catalogueProfile.priceBand,
                      toyworldProfile.priceBand,
                    ],
                    [
                      "Top categories",
                      candidate.catalogueProfile.categories
                        .map((c) => c.name)
                        .join(" · "),
                      toyworldProfile.categories,
                    ],
                  ].map(([label, a, b]) => (
                    <TableRow key={label} className="text-[11px] text-muted-foreground">
                      <TableCell className="px-3.5 py-2.5 font-bold text-foreground">
                        {label}
                      </TableCell>
                      <TableCell className="px-3.5">{a}</TableCell>
                      <TableCell className="px-3.5">{b}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <p className="mt-3 text-[11px] leading-relaxed text-muted-foreground">
              This comparison uses current catalogue profiles only. Price history
              and change tracking for {candidate.name} begin after monitoring
              starts.
            </p>
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
