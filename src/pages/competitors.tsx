import { useState } from "react"
import { useNavigate } from "react-router-dom"
import {
  ArrowRight,
  Boxes,
  GitCompareArrows,
  Package,
  TriangleAlert,
  type LucideIcon,
} from "lucide-react"
import { toast } from "sonner"

import { competitorKpis, type CompetitorRow } from "@/lib/competitors-data"
import { scanToastMessage } from "@/lib/format"
import { useUiState } from "@/lib/ui-store"
import { useWorkspace } from "@/lib/workspace-store"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { AIInsightCard } from "@/components/shared/ai-insight-card"
import {
  CompanyDiscoveryRow,
  type DiscoveryTone,
} from "@/components/shared/company-discovery-row"
import { EmptyState } from "@/components/shared/empty-state"
import { KpiCard, type KpiTone } from "@/components/shared/kpi-card"
import { AddCompetitorDialog } from "@/components/competitors/add-competitor-dialog"
import { CompetitorsTable } from "@/components/competitors/competitors-table"
import { MonitoringHealth } from "@/components/competitors/monitoring-health"
import { MonitoringSettingsDrawer } from "@/components/competitors/monitoring-settings-drawer"
import { RecentActivity } from "@/components/competitors/recent-activity"

const kpiIcons: Record<string, LucideIcon> = {
  competitors: Boxes,
  products: Package,
  changes: GitCompareArrows,
  attention: TriangleAlert,
}

export function CompetitorsPage() {
  const navigate = useNavigate()
  const { scanning } = useUiState()
  const {
    competitors,
    discoveryCandidates,
    runScan,
    pauseCompetitor,
    resumeCompetitor,
    removeCompetitor,
    monitorCandidate,
  } = useWorkspace()
  const [settingsRow, setSettingsRow] = useState<CompetitorRow | null>(null)
  const [pendingCandidate, setPendingCandidate] = useState<string | null>(null)

  const suggestions = discoveryCandidates
    .filter((c) => c.status !== "dismissed")
    .slice(0, 3)

  const startScan = async (row: CompetitorRow) => {
    if (scanning) return
    toast.info("Scan started", { description: `Scanning ${row.name}…` })
    const result = await runScan(row.name)
    const message = scanToastMessage(result)
    toast.success(message.title, { description: message.description })
  }

  const pauseResume = async (row: CompetitorRow) => {
    if (row.status === "paused") {
      await resumeCompetitor(row.slug)
      toast.success("Monitoring resumed", { description: row.name })
    } else {
      await pauseCompetitor(row.slug)
      toast.info("Monitoring paused", { description: row.name })
    }
  }

  const monitor = async (slug: string, name: string) => {
    if (pendingCandidate) return
    setPendingCandidate(slug)
    try {
      await monitorCandidate(slug)
      toast.success("Competitor added", {
        description: `Now monitoring ${name} — initial snapshot queued.`,
      })
    } finally {
      setPendingCandidate(null)
    }
  }

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <section className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">Competitors</h1>
          <p className="mt-1 text-xs text-muted-foreground">
            Monitor competitor catalogues, pricing, stock and market activity.
          </p>
        </div>
        <AddCompetitorDialog onView={(slug) => navigate(`/competitors/${slug}`)} />
      </section>

      <section className="grid grid-cols-2 gap-3.5 xl:grid-cols-4">
        {competitorKpis.map((k) => (
          <KpiCard
            key={k.id}
            icon={kpiIcons[k.id]}
            tone={k.tone as KpiTone}
            value={k.value}
            label={k.label}
          />
        ))}
      </section>

      <AIInsightCard
        title="Portfolio Intelligence"
        ctaLabel="View full analysis"
        onCta={() =>
          navigate("/ask-ai", {
            state: {
              context: { scope: "all-competitors" },
              prompt: "Analyse portfolio activity across my competitors",
            },
          })
        }
      >
        <strong className="text-foreground">ToyWorld.co.uk</strong> generated
        55% of all detected competitor changes today. Most activity is
        concentrated in <strong className="text-foreground">Outdoor Toys</strong>{" "}
        and <strong className="text-foreground">Educational Toys</strong>.
        HappyToyHouse.com requires attention because several product pages could
        not be scanned.
      </AIInsightCard>

      {competitors.length === 0 ? (
        <Card className="rounded-xl shadow-sm">
          <EmptyState
            icon={Boxes}
            heading="No competitors monitored"
            text="Add your first competitor to start collecting intelligence."
          />
        </Card>
      ) : (
        <CompetitorsTable
          rows={competitors}
          onRemoveRow={async (slug) => {
            const name = competitors.find((c) => c.slug === slug)?.name
            await removeCompetitor(slug)
            toast.info("Competitor removed", {
              description: `${name ?? slug} is no longer monitored. Historical data removal is a separate action in Settings.`,
            })
          }}
          onRunScan={startScan}
          onPauseResume={pauseResume}
          onSettings={setSettingsRow}
        />
      )}

      <section className="grid gap-4 xl:grid-cols-2 xl:items-start">
        <MonitoringHealth />
        <RecentActivity />
      </section>

      <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-sm font-bold">
            Competitors you may be missing
          </CardTitle>
          <CardDescription className="text-xs">
            Companies similar to those you already monitor.
          </CardDescription>
        </CardHeader>
        {suggestions.map((d) => (
          <CompanyDiscoveryRow
            key={d.slug}
            name={d.name}
            match={d.match}
            tone={d.tone as DiscoveryTone}
            monitoring={d.status === "monitoring"}
            pending={pendingCandidate === d.slug}
            onToggle={() => monitor(d.slug, d.name)}
          />
        ))}
        <CardFooter className="border-t p-0">
          <Button
            variant="ghost"
            onClick={() => navigate("/discovery")}
            className="h-11 w-full rounded-none text-[11px] font-bold text-primary"
          >
            Explore competitor discovery <ArrowRight className="size-3.5" />
          </Button>
        </CardFooter>
      </Card>

      <MonitoringSettingsDrawer
        competitor={settingsRow}
        onClose={() => setSettingsRow(null)}
      />
    </main>
  )
}
