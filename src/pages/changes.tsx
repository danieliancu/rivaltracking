import { useEffect, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import {
  Activity,
  BadgePercent,
  Download,
  PackageX,
  Sparkles,
  TrendingDown,
  TrendingUp,
  type LucideIcon,
} from "lucide-react"
import { toast } from "sonner"

import {
  changeKpis,
  changePatterns,
  type ChangeEvent,
  type ChangePattern,
} from "@/lib/changes-data"
import {
  changeFiltersFromParams,
  changesCsv,
  filterChanges,
} from "@/lib/change-filters"
import { downloadCsv } from "@/lib/csv"
import { useWorkspace } from "@/lib/workspace-store"
import { Button } from "@/components/ui/button"
import { AIInsightCard } from "@/components/shared/ai-insight-card"
import { KpiCard, type KpiTone } from "@/components/shared/kpi-card"
import { ActiveCompetitors } from "@/components/changes/active-competitors"
import { ChangeActivity } from "@/components/changes/change-activity"
import { ChangeDetailDrawer } from "@/components/changes/change-detail-drawer"
import { ChangeEventsTable } from "@/components/changes/change-events-table"
import { ChangePatterns } from "@/components/changes/change-patterns"

const kpiIcons: Record<string, LucideIcon> = {
  activity: Activity,
  down: TrendingDown,
  up: TrendingUp,
  stock: PackageX,
  new: Sparkles,
  promo: BadgePercent,
}

export function ChangesPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { changeEvents, competitorName } = useWorkspace()
  const [pattern, setPattern] = useState<ChangePattern | null>(null)
  const [detailEvent, setDetailEvent] = useState<ChangeEvent | null>(null)

  /* Deep link: /changes?pattern=outdoor-campaign applies that pattern. */
  useEffect(() => {
    const id = searchParams.get("pattern")
    if (!id) return
    const match = changePatterns.find((p) => p.id === id)
    if (match) setPattern(match)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const exportFiltered = () => {
    const filters = changeFiltersFromParams(searchParams, competitorName)
    const csv = changesCsv(filterChanges(changeEvents, filters))
    downloadCsv("competeiq-changes.csv", csv.headers, csv.rows)
    toast.success("Export ready", {
      description: `${csv.rows.length} changes exported to CSV.`,
    })
  }

  const askAI = () => {
    const filters = changeFiltersFromParams(searchParams, competitorName)
    navigate("/ask-ai", {
      state: {
        context: {
          competitor:
            filters.competitor !== "All competitors"
              ? filters.competitor
              : undefined,
          category:
            filters.category !== "All categories" ? filters.category : undefined,
        },
        prompt: "What changed at my competitors and what should I do about it?",
      },
    })
  }

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <section className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">Changes</h1>
          <p className="mt-1 text-xs text-muted-foreground">
            Track every meaningful change detected across your competitors.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={exportFiltered}
            className="h-9 rounded-lg bg-card text-xs font-bold"
          >
            <Download className="size-4" /> Export
          </Button>
          <Button
            onClick={askAI}
            className="h-9 rounded-lg text-xs font-bold shadow-md shadow-primary/25"
          >
            <Sparkles className="size-4" /> Ask AI about changes
          </Button>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-3.5 md:grid-cols-3 xl:grid-cols-6">
        {changeKpis.map((k) => (
          <KpiCard
            key={k.id}
            icon={kpiIcons[k.icon]}
            tone={k.tone as KpiTone}
            value={k.value}
            label={k.label}
          />
        ))}
      </section>

      <AIInsightCard
        title="AI Change Summary"
        ctaLabel="View strategic analysis"
        onCta={() =>
          navigate("/ask-ai", {
            state: {
              context: { competitor: "ToyWorld.co.uk", period: "Last 7 days" },
              prompt: "Analyse these changes",
            },
          })
        }
      >
        <strong className="text-foreground">ToyWorld.co.uk</strong> generated
        the highest level of activity today, accounting for 55% of all detected
        changes. Most price reductions are concentrated in{" "}
        <strong className="text-foreground">Outdoor Toys</strong>, while
        Educational Toys show increased new-product activity across multiple
        competitors.
        <br />
        <br />
        This pattern may indicate a seasonal promotion combined with catalogue
        expansion ahead of a new campaign.
      </AIInsightCard>

      <ChangePatterns onApplyPattern={setPattern} />

      <ChangeEventsTable
        pattern={pattern}
        onOpenDetails={setDetailEvent}
        urlSync
      />

      <section className="grid gap-4 xl:grid-cols-2 xl:items-start">
        <ChangeActivity />
        <ActiveCompetitors />
      </section>

      <ChangeDetailDrawer
        event={detailEvent}
        onClose={() => setDetailEvent(null)}
      />
    </main>
  )
}
