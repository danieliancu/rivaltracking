import { Check, ChevronDown, Store } from "lucide-react"

import { overviewByRange } from "@/lib/data"
import { useUiState } from "@/lib/ui-store"
import { useWorkspace } from "@/lib/workspace-store"
import { AiSummary } from "@/components/dashboard/ai-summary"
import { AnalyticsCharts } from "@/components/dashboard/analytics-charts"
import { ChangesTable } from "@/components/dashboard/changes-table"
import { Discoveries } from "@/components/dashboard/discoveries"
import { KpiCards } from "@/components/dashboard/kpi-cards"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function OverviewPage() {
  const { competitors } = useWorkspace()
  const { dateRange, selectedCompetitor, setSelectedCompetitor } = useUiState()

  const competitor =
    competitors.find((c) => c.slug === selectedCompetitor) ?? competitors[0]
  const dataset = overviewByRange[dateRange]

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <section className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">
            Competitor Dashboard
          </h1>
          <p className="mt-1 text-xs text-muted-foreground">
            Real-time intelligence across your monitored competitors.
          </p>
        </div>

        {competitor && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                className="h-10 rounded-full bg-card pl-1.5 shadow-sm"
              >
                <span className="flex size-7 items-center justify-center rounded-full bg-accent text-accent-foreground">
                  <Store className="size-3.5" />
                </span>
                <span className="text-xs font-bold">{competitor.name}</span>
                <Badge
                  variant="secondary"
                  className="hidden rounded-full text-[10px] font-bold text-muted-foreground sm:inline-flex"
                >
                  {competitor.market}
                </Badge>
                <ChevronDown className="size-4 text-muted-foreground" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-64">
              <DropdownMenuLabel className="text-xs text-muted-foreground">
                Monitored competitors
              </DropdownMenuLabel>
              {competitors.map((c) => (
                <DropdownMenuItem
                  key={c.slug}
                  onClick={() => setSelectedCompetitor(c.slug)}
                  className="justify-between"
                >
                  <span>
                    <span className="block text-xs font-bold">{c.name}</span>
                    <span className="mt-0.5 block text-[10px] text-muted-foreground">
                      {c.market}
                    </span>
                  </span>
                  {c.slug === competitor.slug && <Check className="size-4" />}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </section>

      <KpiCards kpis={dataset.kpis} />
      <AiSummary />
      <AnalyticsCharts />

      <section className="grid gap-4 xl:grid-cols-[2fr_1fr]">
        <ChangesTable competitor={competitor?.name ?? "your competitors"} />
        <Discoveries />
      </section>
    </main>
  )
}
