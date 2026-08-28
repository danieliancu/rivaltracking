import { Check, Store } from "lucide-react"

import type { DiscoveryCandidate } from "@/lib/discovery-data"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"

export function WhyMatchDrawer({
  candidate,
  onClose,
  onMonitor,
}: {
  candidate: DiscoveryCandidate | null
  onClose: () => void
  onMonitor: (slug: string) => void
}) {
  return (
    <Sheet open={!!candidate} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full gap-0 overflow-y-auto sm:max-w-lg">
        <SheetHeader className="pb-3">
          <SheetTitle className="text-base font-bold">
            {candidate?.name}
          </SheetTitle>
          <SheetDescription className="flex flex-wrap items-center gap-2 text-xs">
            Why this match?
            <Badge
              variant="outline"
              className="rounded-full border-info/25 bg-info/10 px-2 py-0.5 text-[11px] font-bold text-info"
            >
              {candidate?.match}% match
            </Badge>
          </SheetDescription>
        </SheetHeader>

        {candidate && (
          <div className="flex flex-col gap-4 px-4 pb-6">
            <div className="rounded-xl border p-3.5">
              <p className="mb-2 text-xs font-bold">Match evidence</p>
              <div className="flex flex-col gap-2">
                {candidate.whyMatch.map((reason) => (
                  <div
                    key={reason}
                    className="flex items-start gap-2 text-[11px] leading-relaxed text-foreground/80"
                  >
                    <Check className="mt-0.5 size-3.5 shrink-0 text-success" />
                    {reason}
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-xl border p-3.5">
              <p className="mb-2 flex items-center gap-1.5 text-xs font-bold">
                <Store className="size-3.5 text-muted-foreground" /> Catalogue profile
              </p>
              <div className="grid grid-cols-2 gap-x-3 gap-y-2.5 text-xs">
                <div>
                  <span className="block text-[11px] text-muted-foreground">
                    Products
                  </span>
                  <span className="mt-0.5 block font-medium">
                    {candidate.catalogueProfile.products.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="block text-[11px] text-muted-foreground">
                    Price band
                  </span>
                  <span className="mt-0.5 block font-medium">
                    {candidate.catalogueProfile.priceBand}
                  </span>
                </div>
                <div className="col-span-2">
                  <span className="block text-[11px] text-muted-foreground">
                    Top categories
                  </span>
                  <span className="mt-0.5 block font-medium">
                    {candidate.catalogueProfile.categories
                      .map((c) => `${c.name} (${c.count})`)
                      .join(" · ")}
                  </span>
                </div>
              </div>
            </div>

            <p className="text-[11px] leading-relaxed text-muted-foreground">
              This profile comes from the discovery comparison. Price and stock
              history become available after monitoring starts.
            </p>

            {candidate.status !== "monitoring" && (
              <Button
                onClick={() => {
                  onClose()
                  onMonitor(candidate.slug)
                }}
                className="h-9 w-fit rounded-lg text-xs font-bold"
              >
                Monitor {candidate.name}
              </Button>
            )}
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
