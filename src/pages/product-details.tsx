import { useState } from "react"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"
import {
  ArrowLeft,
  ArrowRight,
  Bell,
  ExternalLink,
  GitCompareArrows,
  Package,
  Sparkles,
} from "lucide-react"

import { useWorkspace } from "@/lib/workspace-store"
import type { ChangeEvent } from "@/lib/changes-data"
import type { ChangeKind } from "@/components/shared/change-badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AIInsightCard } from "@/components/shared/ai-insight-card"
import { ChangeBadge } from "@/components/shared/change-badge"
import { ChangeDetailDrawer } from "@/components/changes/change-detail-drawer"
import { CompareDrawer } from "@/components/products/compare-drawer"
import { EmptyState } from "@/components/shared/empty-state"
import { StockBadge } from "@/components/shared/stock-badge"
import { PriceMovement } from "@/components/products/price-movement"

const sections = [
  { id: "overview", label: "Overview" },
  { id: "price-history", label: "Price History" },
  { id: "stock-history", label: "Stock History" },
  { id: "changes", label: "Changes" },
  { id: "comparison", label: "Competitor Comparison" },
  { id: "ai-analysis", label: "AI Analysis" },
] as const

type SectionId = (typeof sections)[number]["id"]

function ProductEvents({
  events,
  emptyText,
  onOpen,
}: {
  events: ChangeEvent[]
  emptyText: string
  onOpen: (event: ChangeEvent) => void
}) {
  if (events.length === 0) {
    return (
      <Card className="rounded-xl shadow-sm">
        <EmptyState heading="No events recorded" text={emptyText} />
      </Card>
    )
  }
  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-bold">Detected Events</CardTitle>
      </CardHeader>
      <CardContent className="px-0 pb-0">
        <div className="overflow-x-auto">
          <Table className="min-w-[560px]">
            <TableHeader>
              <TableRow>
                {["Change", "Old Value", "New Value", "Impact", "Detected"].map(
                  (h) => (
                    <TableHead key={h} className="px-3.5 text-[10px] font-bold">
                      {h}
                    </TableHead>
                  )
                )}
              </TableRow>
            </TableHeader>
            <TableBody>
              {events.map((e) => (
                <TableRow
                  key={e.id}
                  onClick={() => onOpen(e)}
                  className="cursor-pointer text-[11px] text-muted-foreground"
                >
                  <TableCell className="px-3.5 py-2.5">
                    <ChangeBadge kind={e.kind} label={e.label} />
                  </TableCell>
                  <TableCell className="px-3.5">{e.previous}</TableCell>
                  <TableCell className="px-3.5 font-medium text-foreground">
                    {e.current}
                  </TableCell>
                  <TableCell className="px-3.5 capitalize">{e.impact}</TableCell>
                  <TableCell className="px-3.5">{e.detectedAt}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}

export function ProductDetailsPage() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { products, changeEvents } = useWorkspace()
  const [detailEvent, setDetailEvent] = useState<ChangeEvent | null>(null)
  const [compareOpen, setCompareOpen] = useState(false)

  const row = products.find((r) => r.slug === slug)
  const events = changeEvents.filter((e) => e.product.slug === slug)

  const tabParam = searchParams.get("tab")
  const tab: SectionId = sections.some((s) => s.id === tabParam)
    ? (tabParam as SectionId)
    : "overview"

  const byKinds = (kinds: ChangeKind[]) =>
    events.filter((e) => kinds.includes(e.kind))

  if (!row) {
    return (
      <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
        <Button
          variant="ghost"
          onClick={() => navigate("/products")}
          className="h-8 w-fit gap-1.5 rounded-lg px-2 text-xs font-semibold text-muted-foreground"
        >
          <ArrowLeft className="size-3.5" /> Back to products
        </Button>
        <Card className="rounded-xl shadow-sm">
          <EmptyState
            icon={Package}
            heading="Product not found"
            text="This product is not in your monitored catalogue."
            actionLabel="View products"
            onAction={() => navigate("/products")}
          />
        </Card>
      </main>
    )
  }

  const createAlert = () =>
    navigate("/alerts", {
      state: {
        createAlert: {
          competitor: row.competitor,
          category: row.category,
          product: row.name,
        },
      },
    })

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <Button
        variant="ghost"
        onClick={() => navigate("/products")}
        className="h-8 w-fit gap-1.5 rounded-lg px-2 text-xs font-semibold text-muted-foreground"
      >
        <ArrowLeft className="size-3.5" /> Back to products
      </Button>

      <section className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <span className="flex size-9 items-center justify-center rounded-lg bg-accent text-accent-foreground">
            <Package className="size-4.5" />
          </span>
          <div>
            <h1 className="text-lg font-extrabold tracking-tight">{row.name}</h1>
            <p className="text-[10px] text-muted-foreground">
              {row.sku} · {row.competitor} · {row.category}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <ChangeBadge kind={row.change.kind} label={row.change.label} />
          <StockBadge inStock={row.inStock} />
          <Button
            variant="outline"
            size="sm"
            onClick={createAlert}
            className="h-8 rounded-lg bg-card text-[11px] font-bold"
          >
            <Bell className="size-3.5" /> Create alert
          </Button>
          <Button
            size="sm"
            onClick={() => navigate(`/ask-ai?product=${row.slug}`)}
            className="h-8 rounded-lg text-[11px] font-bold"
          >
            <Sparkles className="size-3.5" /> Ask AI
          </Button>
        </div>
      </section>

      <Tabs
        value={tab}
        onValueChange={(value) =>
          setSearchParams(value === "overview" ? {} : { tab: value }, {
            replace: true,
          })
        }
      >
        <TabsList className="h-9 rounded-lg">
          {sections.map((s) => (
            <TabsTrigger
              key={s.id}
              value={s.id}
              className="rounded-md px-3 text-[11px] font-semibold data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
            >
              {s.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {tab === "overview" && (
        <>
          <section className="grid grid-cols-2 gap-3.5 xl:grid-cols-4">
            {(
              [
                ["Current price", `£${row.currentPrice.toFixed(2)}`],
                [
                  "Previous price",
                  row.previousPrice === null
                    ? "—"
                    : `£${row.previousPrice.toFixed(2)}`,
                ],
                ["Last change", row.lastChange],
                ["Discovered", row.discoveredAt],
              ] as const
            ).map(([label, value]) => (
              <Card key={label} className="gap-0 rounded-xl p-4 shadow-sm">
                <span className="block text-[19px] font-bold tracking-tight">
                  {value}
                </span>
                <span className="mt-0.5 block text-[11px] font-semibold text-muted-foreground">
                  {label}
                </span>
              </Card>
            ))}
          </section>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`/changes?product=${row.slug}`)}
              className="h-8 rounded-lg bg-card text-[11px] font-bold"
            >
              View supporting changes <ArrowRight className="size-3.5" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                window.open(row.sourceUrl, "_blank", "noopener,noreferrer")
              }
              className="h-8 rounded-lg bg-card text-[11px] font-bold"
            >
              <ExternalLink className="size-3.5" /> Open source page
            </Button>
            {row.matched && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCompareOpen(true)}
                className="h-8 rounded-lg bg-card text-[11px] font-bold"
              >
                <GitCompareArrows className="size-3.5" /> Compare {row.matched.count}{" "}
                listings
              </Button>
            )}
          </div>
          <ProductEvents
            events={events}
            emptyText="Change history begins after the second successful scan."
            onOpen={setDetailEvent}
          />
        </>
      )}

      {tab === "price-history" && (
        <>
          <PriceMovement />
          <ProductEvents
            events={byKinds(["drop", "increase", "promo", "promo-end"])}
            emptyText="No price changes recorded for this product yet."
            onOpen={setDetailEvent}
          />
        </>
      )}

      {tab === "stock-history" && (
        <ProductEvents
          events={byKinds(["oos", "back", "missing"])}
          emptyText="No stock changes recorded for this product yet."
          onOpen={setDetailEvent}
        />
      )}

      {tab === "changes" && (
        <>
          <ProductEvents
            events={events}
            emptyText="Change history begins after the second successful scan."
            onOpen={setDetailEvent}
          />
          <Button
            variant="ghost"
            onClick={() => navigate(`/changes?product=${row.slug}`)}
            className="h-9 w-fit rounded-lg px-2 text-xs font-bold text-primary"
          >
            View in Changes <ArrowRight className="size-3.5" />
          </Button>
        </>
      )}

      {tab === "comparison" &&
        (row.matched ? (
          <>
            <Card className="rounded-xl p-4 shadow-sm">
              <p className="text-xs leading-relaxed text-foreground/70">
                {row.matched.insight}
              </p>
              <Button
                size="sm"
                onClick={() => setCompareOpen(true)}
                className="mt-3 h-8 w-fit rounded-lg text-[11px] font-bold"
              >
                <GitCompareArrows className="size-3.5" /> Compare{" "}
                {row.matched.count} competitor listings
              </Button>
            </Card>
          </>
        ) : (
          <Card className="rounded-xl shadow-sm">
            <EmptyState
              icon={GitCompareArrows}
              heading="No matched listings"
              text="Product matching has not found this product at other competitors yet."
            />
          </Card>
        ))}

      {tab === "ai-analysis" && (
        <AIInsightCard
          title={`AI Analysis — ${row.name}`}
          ctaLabel="Ask AI about this product"
          onCta={() => navigate(`/ask-ai?product=${row.slug}`)}
        >
          {events.length > 0 ? (
            <>
              This product recorded{" "}
              <strong className="text-foreground">
                {events.length} verified {events.length === 1 ? "change" : "changes"}
              </strong>{" "}
              recently, the latest being{" "}
              <strong className="text-foreground">
                {events[0].label.toLowerCase()}
              </strong>{" "}
              detected {events[0].detected}. Ask AI can explain what this means
              in the context of {row.competitor}'s wider activity.
            </>
          ) : (
            <>
              No changes have been recorded for this product yet. AI analysis
              becomes meaningful after change history begins with the second
              successful scan.
            </>
          )}
        </AIInsightCard>
      )}

      <ChangeDetailDrawer event={detailEvent} onClose={() => setDetailEvent(null)} />
      <CompareDrawer
        product={compareOpen ? row : null}
        onClose={() => setCompareOpen(false)}
      />
    </main>
  )
}
