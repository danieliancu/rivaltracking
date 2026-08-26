import { useNavigate, useParams, useSearchParams } from "react-router-dom"
import { ArrowLeft, ArrowRight, Boxes } from "lucide-react"

import { useWorkspace } from "@/lib/workspace-store"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AIInsightCard } from "@/components/shared/ai-insight-card"
import { CompetitorIdentity } from "@/components/shared/competitor-identity"
import { EmptyState } from "@/components/shared/empty-state"
import { StatusBadge } from "@/components/shared/status-badge"
import { ChangesTable } from "@/components/dashboard/changes-table"
import { PriceMovement } from "@/components/products/price-movement"
import { ProductsTable } from "@/components/products/products-table"

const sections = [
  { id: "overview", label: "Overview" },
  { id: "products", label: "Products" },
  { id: "price-history", label: "Price History" },
  { id: "stock", label: "Stock" },
  { id: "promotions", label: "Promotions" },
  { id: "ai-analysis", label: "AI Analysis" },
] as const

type SectionId = (typeof sections)[number]["id"]

export function CompetitorDetailsPage() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { competitors } = useWorkspace()
  const row = competitors.find((r) => r.slug === slug)

  const tabParam = searchParams.get("tab")
  const tab: SectionId = sections.some((s) => s.id === tabParam)
    ? (tabParam as SectionId)
    : "overview"

  if (!row) {
    return (
      <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
        <Button
          variant="ghost"
          onClick={() => navigate("/competitors")}
          className="h-8 w-fit gap-1.5 rounded-lg px-2 text-xs font-semibold text-muted-foreground"
        >
          <ArrowLeft className="size-3.5" /> Back to competitors
        </Button>
        <Card className="rounded-xl shadow-sm">
          <EmptyState
            icon={Boxes}
            heading="Competitor not found"
            text="This competitor is not monitored in your workspace."
            actionLabel="View competitors"
            onAction={() => navigate("/competitors")}
          />
        </Card>
      </main>
    )
  }

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <Button
        variant="ghost"
        onClick={() => navigate("/competitors")}
        className="h-8 w-fit gap-1.5 rounded-lg px-2 text-xs font-semibold text-muted-foreground"
      >
        <ArrowLeft className="size-3.5" /> Back to competitors
      </Button>

      <section className="flex items-center justify-between gap-4">
        <CompetitorIdentity name={row.name} url={row.url} />
        <StatusBadge status={row.status} />
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
                ["Products monitored", row.products?.toLocaleString() ?? "—"],
                ["Changes today", row.changesToday?.toString() ?? "—"],
                [
                  "Price changes",
                  row.priceDrops === null
                    ? "—"
                    : `${row.priceDrops} ↓ / ${row.priceIncreases} ↑`,
                ],
                ["Last scan", row.lastScan],
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
          <ChangesTable competitor={row.name} />
        </>
      )}

      {tab === "products" && (
        <ProductsTable lockedCompetitor={row.slug} urlSync={false} />
      )}

      {tab === "price-history" && (
        <>
          <PriceMovement />
          <ChangesTable
            competitor={row.name}
            kinds={["drop", "increase"]}
            title="Price Change Events"
            description={`Detected price movements at ${row.name}`}
          />
        </>
      )}

      {tab === "stock" && (
        <ChangesTable
          competitor={row.name}
          kinds={["oos", "back", "missing"]}
          title="Stock Activity"
          description={`Stock-outs and restocks detected at ${row.name}`}
        />
      )}

      {tab === "promotions" && (
        <ChangesTable
          competitor={row.name}
          kinds={["promo", "promo-end"]}
          title="Promotion Activity"
          description={`Promotions detected at ${row.name}`}
        />
      )}

      {tab === "ai-analysis" && (
        <>
          <AIInsightCard
            title={`AI Analysis — ${row.name}`}
            ctaLabel="Open full Ask AI"
            onCta={() => navigate(`/ask-ai?competitor=${row.slug}`)}
          >
            {row.changesToday === null ? (
              <>
                {row.name} is still building its initial snapshot. AI analysis
                becomes available after the second successful scan, when change
                history begins.
              </>
            ) : (
              <>
                <strong className="text-foreground">{row.name}</strong> recorded{" "}
                <strong className="text-foreground">
                  {row.changesToday} changes
                </strong>{" "}
                today, including {row.priceDrops} price reductions and{" "}
                {row.stockChanges} stock movements. Ask AI can break down which
                categories drive this activity and how it compares with your
                other competitors.
              </>
            )}
          </AIInsightCard>
          <ChangesTable
            competitor={row.name}
            title="Evidence — Recent Changes"
            description={`Verified events behind the analysis for ${row.name}`}
          />
        </>
      )}

      <Button
        variant="ghost"
        onClick={() => navigate(`/changes?competitor=${row.slug}`)}
        className="h-9 w-fit rounded-lg px-2 text-xs font-bold text-primary"
      >
        View all changes for {row.name} <ArrowRight className="size-3.5" />
      </Button>
    </main>
  )
}
