import { useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { toast } from "sonner"
import {
  ArrowLeft,
  ArrowRight,
  BadgePercent,
  Boxes,
  Clock3,
  Download,
  FileText,
  GitCompareArrows,
  PackageX,
  RefreshCw,
  Sparkles,
  Tags,
  TrendingDown,
  TrendingUp,
  TriangleAlert,
  type LucideIcon,
} from "lucide-react"
import { Bar, BarChart, CartesianGrid, LabelList, Line, LineChart, XAxis, YAxis } from "recharts"

import { weeklyReport } from "@/lib/reports-data"
import { reportCsv } from "@/lib/report-csv"
import { downloadCsv } from "@/lib/csv"
import { useWorkspace } from "@/lib/workspace-store"
import { cn } from "@/lib/utils"
import { EmptyState } from "@/components/shared/empty-state"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { AIInsightCard } from "@/components/shared/ai-insight-card"
import { KpiCard, type KpiTone } from "@/components/shared/kpi-card"
import { ReportStatusBadge } from "@/components/reports/report-status-badge"

const metricIcons: Record<string, LucideIcon> = {
  changes: GitCompareArrows,
  new: Sparkles,
  drops: TrendingDown,
  increases: TrendingUp,
  stockouts: PackageX,
  promos: BadgePercent,
}

const pricingChartConfig = {
  decreases: { label: "Price decreases", color: "var(--success)" },
  increases: { label: "Price increases", color: "var(--destructive)" },
} satisfies ChartConfig

const categoryChartConfig = {
  changes: { label: "Changes", color: "var(--chart-1)" },
} satisfies ChartConfig

function AiNote({ text }: { text: string }) {
  return (
    <div className="bg-ai-subtle flex items-start gap-2.5 rounded-xl border border-purple/20 p-3">
      <span className="flex size-6 shrink-0 items-center justify-center rounded-md bg-purple/10 text-purple">
        <Sparkles className="size-3" />
      </span>
      <p className="text-[11px] leading-relaxed text-foreground/70">{text}</p>
    </div>
  )
}

function IntelligenceCard({
  section,
}: {
  section: { title: string; facts: { label: string; value: string }[]; aiNote: string }
}) {
  return (
    <Card className="gap-3 rounded-xl p-4 shadow-sm">
      <h3 className="text-sm font-bold">{section.title}</h3>
      <div className="grid grid-cols-2 gap-x-3 gap-y-2.5">
        {section.facts.map((f) => (
          <div key={f.label}>
            <span className="block text-sm font-medium">{f.value}</span>
            <span className="mt-0.5 block text-[11px] text-muted-foreground">
              {f.label}
            </span>
          </div>
        ))}
      </div>
      <AiNote text={section.aiNote} />
    </Card>
  )
}

export function ReportDetailsPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const { reports, createReport } = useWorkspace()
  const [regenerating, setRegenerating] = useState(false)
  const report = reports.find((x) => x.id === id)
  /* The detailed weekly dataset serves as the mock body for every report;
     header metadata comes from the actual report record. */
  const r = weeklyReport

  if (!report) {
    return (
      <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
        <Button
          variant="ghost"
          onClick={() => navigate("/reports")}
          className="h-8 w-fit gap-1.5 rounded-lg px-2 text-xs font-semibold text-muted-foreground"
        >
          <ArrowLeft className="size-3.5" /> Back to reports
        </Button>
        <Card className="rounded-xl shadow-sm">
          <EmptyState
            icon={FileText}
            heading="Report not found"
            text="This report does not exist or has been deleted."
            actionLabel="View reports"
            onAction={() => navigate("/reports")}
          />
        </Card>
      </main>
    )
  }

  const exportCsv = () => {
    const csv = reportCsv(report)
    downloadCsv(csv.filename, csv.headers, csv.rows)
    toast.success("Export ready", {
      description: `${report.name} exported to CSV.`,
    })
  }

  const regenerate = async () => {
    if (regenerating) return
    setRegenerating(true)
    try {
      const fresh = await createReport({
        typeId: report.typeId,
        type: report.type,
        competitors: report.competitors,
        period: report.period,
        category: report.category,
        changeType: report.changeType,
        aiAnalysis: report.aiAnalysis ?? true,
      })
      toast.success("Report regenerated", {
        description: "A new version was created — the original is unchanged.",
      })
      navigate(`/reports/${fresh.id}`)
    } finally {
      setRegenerating(false)
    }
  }

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <Button
        variant="ghost"
        onClick={() => navigate("/reports")}
        className="h-8 w-fit gap-1.5 rounded-lg px-2 text-xs font-semibold text-muted-foreground"
      >
        <ArrowLeft className="size-3.5" /> Back to reports
      </Button>

      <section className="flex flex-col items-start justify-between gap-4 xl:flex-row xl:items-center">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-2xl font-extrabold tracking-tight">
              {report.name}
            </h1>
            <ReportStatusBadge status={report.status} />
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            {report.period} · {report.competitors} competitors · Created{" "}
            {report.created}
          </p>
          <p className="mt-1 flex items-center gap-1 text-[11px] text-muted-foreground">
            <Clock3 className="size-3" /> Data through: {report.dataThrough}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            onClick={regenerate}
            disabled={regenerating}
            className="h-9 rounded-lg bg-card text-xs font-bold"
          >
            <RefreshCw className={cn("size-4", regenerating && "animate-spin")} />
            {regenerating ? "Regenerating…" : "Regenerate report"}
          </Button>
          <Button
            variant="outline"
            onClick={() =>
              toast.info("PDF generation will be handled by the report backend.", {
                description: "Export to CSV is available in the meantime.",
              })
            }
            className="h-9 rounded-lg bg-card text-xs font-bold"
          >
            <Download className="size-4" /> Download PDF
          </Button>
          <Button
            variant="outline"
            onClick={exportCsv}
            className="h-9 rounded-lg bg-card text-xs font-bold"
          >
            <FileText className="size-4" /> Export CSV
          </Button>
        </div>
      </section>

      <AIInsightCard
        title="Executive Summary"
        ctaLabel="Ask AI"
        onCta={() =>
          navigate("/ask-ai", {
            state: {
              prompt: `Summarise the key findings of ${report.name}`,
            },
          })
        }
      >
        {r.executiveSummary}
        <br />
        <br />
        <strong className="text-foreground">Key takeaway:</strong>{" "}
        {r.keyTakeaway}
      </AIInsightCard>

      <section className="grid grid-cols-2 gap-3.5 md:grid-cols-3 xl:grid-cols-6">
        {r.metrics.map((m) => (
          <KpiCard
            key={m.id}
            icon={metricIcons[m.id]}
            tone={m.tone as KpiTone}
            value={m.value}
            label={m.label}
          />
        ))}
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-bold">Major Developments</h2>
        <div className="grid gap-3.5 xl:grid-cols-3">
          {r.developments.map((d) => (
            <Card key={d.rank} className="gap-3 rounded-xl p-4 shadow-sm">
              <div className="flex items-center gap-2.5">
                <span
                  className={cn(
                    "flex size-8.5 shrink-0 items-center justify-center rounded-lg text-sm font-bold",
                    d.tone
                  )}
                >
                  {d.rank}
                </span>
                <span className="text-sm font-medium">{d.title}</span>
              </div>
              <ul className="flex flex-col gap-1 text-[11px] text-muted-foreground">
                {d.facts.map((f) => (
                  <li key={f}>{f}</li>
                ))}
              </ul>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate(d.evidence.to)}
                className="h-8 w-fit rounded-lg text-[11px] font-bold"
              >
                {d.evidence.label} <ArrowRight className="size-3.5" />
              </Button>
            </Card>
          ))}
        </div>
      </section>

      <Card className="rounded-xl shadow-sm">
        <CardHeader>
          <CardTitle className="text-sm font-bold">Pricing Intelligence</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 xl:grid-cols-[240px_1fr]">
          <div className="flex flex-col gap-3">
            {r.pricing.facts.map((f) => (
              <div key={f.label}>
                <span className={cn("block text-lg font-bold tracking-tight", f.tone)}>
                  {f.value}
                </span>
                <span className="text-[11px] text-muted-foreground">
                  {f.label}
                </span>
              </div>
            ))}
          </div>
          <div className="flex min-w-0 flex-col gap-3">
            <ChartContainer
              config={pricingChartConfig}
              className="aspect-auto h-[200px] w-full"
            >
              <LineChart data={r.pricing.series} margin={{ top: 8, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 10 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10 }} width={28} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Line type="monotone" dataKey="decreases" stroke="var(--color-decreases)" strokeWidth={2.5} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="increases" stroke="var(--color-increases)" strokeWidth={2.5} strokeDasharray="6 4" dot={false} isAnimationActive={false} />
              </LineChart>
            </ChartContainer>
            <AiNote text={r.pricing.aiNote} />
          </div>
        </CardContent>
      </Card>

      <section className="grid gap-4 xl:grid-cols-3 xl:items-start">
        <IntelligenceCard section={r.catalogue} />
        <IntelligenceCard section={r.stock} />
        <IntelligenceCard section={r.promotions} />
      </section>

      <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-sm font-bold">Competitor Comparison</CardTitle>
        </CardHeader>
        <CardContent className="px-0 pb-0">
          <div className="overflow-x-auto">
            <Table className="min-w-[860px]">
              <TableHeader>
                <TableRow>
                  {[
                    "Competitor",
                    "Products",
                    "New Products",
                    "Price Drops",
                    "Price Increases",
                    "Stock-outs",
                    "Promotions",
                    "Total Changes",
                  ].map((h, i) => (
                    <TableHead key={i} className="px-3.5 text-[10px] font-bold">
                      {h}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {r.competitorComparison.map((c) => (
                  <TableRow key={c.name} className="text-[11px] text-muted-foreground">
                    <TableCell className="px-3.5 py-2.5">
                      <span className="flex items-center gap-2.5">
                        <span className="flex size-8.5 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground">
                          <Boxes className="size-4" />
                        </span>
                        <span className="text-sm font-medium text-foreground">
                          {c.name}
                        </span>
                      </span>
                    </TableCell>
                    <TableCell className="px-3.5 font-medium text-foreground">
                      {c.products.toLocaleString()}
                    </TableCell>
                    <TableCell className="px-3.5">{c.newProducts}</TableCell>
                    <TableCell className="px-3.5 font-medium text-success">
                      {c.drops}
                    </TableCell>
                    <TableCell className="px-3.5 font-medium text-destructive">
                      {c.increases}
                    </TableCell>
                    <TableCell className="px-3.5">{c.stockouts}</TableCell>
                    <TableCell className="px-3.5">{c.promos}</TableCell>
                    <TableCell className="px-3.5 font-medium text-foreground">
                      {c.total}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <section className="grid gap-4 xl:grid-cols-2 xl:items-start">
        <Card className="rounded-xl shadow-sm">
          <CardHeader>
            <CardTitle className="text-sm font-bold">Category Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer
              config={categoryChartConfig}
              className="aspect-auto h-[190px] w-full"
            >
              <BarChart
                data={r.categoryComparison}
                layout="vertical"
                margin={{ left: 4, right: 34 }}
              >
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" width={112} axisLine={false} tickLine={false} tick={{ fontSize: 11 }} />
                <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                <Bar dataKey="changes" fill="var(--color-changes)" radius={[0, 5, 5, 0]} barSize={16} isAnimationActive={false}>
                  <LabelList dataKey="changes" position="right" className="fill-foreground" fontSize={10} fontWeight={700} />
                </Bar>
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <div className="flex flex-col gap-4">
          <Card className="gap-3 rounded-xl border-teal/25 p-4 shadow-sm">
            <div className="flex items-center gap-2">
              <span className="flex size-7 items-center justify-center rounded-lg bg-teal/10 text-teal">
                <Sparkles className="size-3.5" />
              </span>
              <h3 className="text-sm font-bold">Potential Opportunities</h3>
            </div>
            {r.opportunities.map((o, i) => (
              <p key={i} className="text-[11px] leading-relaxed text-foreground/70">
                {o}
              </p>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate("/products")}
              className="h-8 w-fit rounded-lg text-[11px] font-bold"
            >
              View pricing data <ArrowRight className="size-3.5" />
            </Button>
          </Card>
          <Card className="gap-3 rounded-xl border-warning/25 p-4 shadow-sm">
            <div className="flex items-center gap-2">
              <span className="flex size-7 items-center justify-center rounded-lg bg-warning/10 text-warning">
                <TriangleAlert className="size-3.5" />
              </span>
              <h3 className="text-sm font-bold">Risks</h3>
            </div>
            {r.risks.map((o, i) => (
              <p key={i} className="text-[11px] leading-relaxed text-foreground/70">
                {o}
              </p>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                navigate("/changes?competitor=toyworld-co-uk&type=price-decrease&range=7d")
              }
              className="h-8 w-fit rounded-lg text-[11px] font-bold"
            >
              View 42 supporting changes <ArrowRight className="size-3.5" />
            </Button>
          </Card>
        </div>
      </section>

      <Card className="gap-3 rounded-xl p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="flex size-7 items-center justify-center rounded-lg bg-info/10 text-info">
            <Tags className="size-3.5" />
          </span>
          <h3 className="text-sm font-bold">Recommended Areas to Review</h3>
        </div>
        <ol className="flex flex-col gap-2">
          {r.recommendedActions.map((a, i) => (
            <li key={a} className="flex items-start gap-2.5 text-xs text-foreground/80">
              <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-accent text-[10px] font-bold text-accent-foreground">
                {i + 1}
              </span>
              {a}
            </li>
          ))}
        </ol>
        <p className="text-[11px] text-muted-foreground">
          CompeteIQ recommends areas to investigate — it does not take business
          actions automatically.
        </p>
      </Card>
    </main>
  )
}
