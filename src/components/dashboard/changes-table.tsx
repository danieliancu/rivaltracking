import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowRight } from "lucide-react"

import { slugForCompetitor } from "@/lib/entities"
import { useWorkspace } from "@/lib/workspace-store"
import type { ChangeEvent } from "@/lib/changes-data"
import type { ChangeKind } from "@/components/shared/change-badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { ChangeBadge } from "@/components/shared/change-badge"
import { ChangeDetailDrawer } from "@/components/changes/change-detail-drawer"
import { EmptyState } from "@/components/shared/empty-state"
import { ProductIdentity } from "@/components/shared/product-identity"
import { StockBadge } from "@/components/shared/stock-badge"

export function ChangesTable({
  competitor,
  kinds,
  title = "Recent Change Events",
  description,
}: {
  competitor: string
  /* Restrict to specific change kinds (e.g. stock or promotion events). */
  kinds?: ChangeKind[]
  title?: string
  description?: string
}) {
  const navigate = useNavigate()
  const { changeEvents } = useWorkspace()
  const [detailEvent, setDetailEvent] = useState<ChangeEvent | null>(null)

  const rows = changeEvents
    .filter(
      (e) => e.competitor === competitor && (!kinds || kinds.includes(e.kind))
    )
    .slice(0, 5)

  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-bold">{title}</CardTitle>
        <CardDescription className="text-xs">
          {description ?? `Latest detected movements across ${competitor}`}
        </CardDescription>
      </CardHeader>
      <CardContent className="px-0">
        <div className="overflow-x-auto">
          {rows.length === 0 ? (
            <EmptyState
              heading="No recent changes"
              text="Change history begins after the second successful scan."
            />
          ) : (
            <Table className="min-w-[760px]">
              <TableHeader>
                <TableRow>
                  <TableHead className="px-3.5 text-[10px] font-bold">Product</TableHead>
                  <TableHead className="px-3.5 text-[10px] font-bold">Change</TableHead>
                  <TableHead className="px-3.5 text-[10px] font-bold">Old Value</TableHead>
                  <TableHead className="px-3.5 text-[10px] font-bold">New Value</TableHead>
                  <TableHead className="px-3.5 text-[10px] font-bold">Stock</TableHead>
                  <TableHead className="px-3.5 text-[10px] font-bold">Category</TableHead>
                  <TableHead className="px-3.5 text-[10px] font-bold">Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((e) => (
                  <TableRow
                    key={e.id}
                    onClick={() => setDetailEvent(e)}
                    className="cursor-pointer text-[11px] text-muted-foreground"
                  >
                    <TableCell className="px-3.5 py-2.5">
                      <ProductIdentity
                        icon={e.product.icon}
                        tone={e.product.tone}
                        name={e.product.name}
                        sku={e.product.sku}
                      />
                    </TableCell>
                    <TableCell className="px-3.5">
                      <ChangeBadge kind={e.kind} label={e.label} />
                    </TableCell>
                    <TableCell className="px-3.5">{e.previous}</TableCell>
                    <TableCell className="px-3.5 font-medium text-foreground">
                      {e.current}
                    </TableCell>
                    <TableCell className="px-3.5">
                      <StockBadge inStock={e.evidence.current.stock === "In stock"} />
                    </TableCell>
                    <TableCell className="px-3.5">{e.category}</TableCell>
                    <TableCell className="px-3.5">{e.detected}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </CardContent>
      <CardFooter className="p-0">
        <Button
          variant="ghost"
          onClick={() =>
            navigate(`/changes?competitor=${slugForCompetitor(competitor)}`)
          }
          className="h-11 w-full rounded-none text-[11px] font-bold text-primary"
        >
          View all changes <ArrowRight className="size-3.5" />
        </Button>
      </CardFooter>

      <ChangeDetailDrawer event={detailEvent} onClose={() => setDetailEvent(null)} />
    </Card>
  )
}
