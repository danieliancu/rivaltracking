import { Fragment } from "react"
import { useNavigate } from "react-router-dom"
import {
  ArrowRight,
  Bell,
  Clock3,
  FileBarChart2,
  GitCompareArrows,
  MoveRight,
  Package,
  ShieldCheck,
  Sparkles,
} from "lucide-react"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"

import { type AIAction, type AIResponseData } from "@/lib/ask-ai-data"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
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

const chartConfig = {
  value: { label: "Changes", color: "var(--chart-1)" },
} satisfies ChartConfig

/* Render **bold** markers from canned bullets. */
function RichText({ text }: { text: string }) {
  const parts = text.split(/\*\*(.+?)\*\*/g)
  return (
    <>
      {parts.map((p, i) =>
        i % 2 === 1 ? (
          <strong key={i} className="font-bold text-foreground">
            {p}
          </strong>
        ) : (
          <Fragment key={i}>{p}</Fragment>
        )
      )}
    </>
  )
}

const actionMeta: Record<AIAction["kind"], { icon: typeof Bell; to: string }> = {
  alert: { icon: Bell, to: "/alerts" },
  report: { icon: FileBarChart2, to: "/reports" },
  changes: { icon: GitCompareArrows, to: "/changes" },
  products: { icon: Package, to: "/products" },
}

export function AIResponse({
  response,
  onFollowUp,
}: {
  response: AIResponseData
  onFollowUp: (question: string) => void
}) {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col gap-3.5 rounded-2xl border bg-card p-4 shadow-sm sm:p-5">
      <div className="flex items-start gap-2.5">
        <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-lg bg-purple/10 text-purple">
          <Sparkles className="size-3.5" />
        </span>
        <div className="min-w-0">
          <h2 className="text-sm font-bold">{response.heading}</h2>
          {response.summary && (
            <p className="mt-1 text-xs leading-relaxed text-foreground/80">
              {response.summary}
            </p>
          )}
        </div>
      </div>

      {response.bullets && (
        <ul className="flex flex-col gap-1 pl-9 text-xs text-muted-foreground">
          {response.bullets.map((b) => (
            <li key={b} className="list-disc">
              <RichText text={b} />
            </li>
          ))}
        </ul>
      )}

      {response.metrics && (
        <div className="rounded-xl border p-3">
          <div className="mb-2 flex items-center gap-1.5">
            <ShieldCheck className="size-3.5 text-success" />
            <span className="text-[11px] font-bold text-muted-foreground">
              Verified data
            </span>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-2.5 sm:grid-cols-4">
            {response.metrics.map((m) => (
              <div key={m.label}>
                <span
                  className={cn(
                    "block text-lg font-bold tracking-tight",
                    m.tone ?? "text-foreground"
                  )}
                >
                  {m.value}
                </span>
                <span className="text-[11px] text-muted-foreground">
                  {m.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {response.productList && (
        <div className="rounded-xl border">
          <p className="border-b px-3.5 py-2.5 text-[11px] font-bold text-muted-foreground">
            {response.productList.title}
          </p>
          {response.productList.items.map((p, i) => (
            <button
              key={p.slug}
              onClick={() => navigate(`/products/${p.slug}`)}
              className="flex w-full items-center gap-2.5 border-b px-3.5 py-2.5 text-left last:border-b-0 hover:bg-muted/50"
            >
              <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-accent text-[10px] font-bold text-accent-foreground">
                {i + 1}
              </span>
              <span className="min-w-0 flex-1 truncate text-sm font-medium">
                {p.name}
              </span>
              <span className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
                <span className="line-through decoration-muted-foreground/40">
                  {p.from}
                </span>
                <MoveRight className="size-3 text-muted-foreground/50" />
                <span className="font-medium text-foreground">{p.to}</span>
              </span>
              <span className="text-[11px] font-bold text-success">{p.pct}</span>
            </button>
          ))}
        </div>
      )}

      {response.comparisonTable && (
        <div className="overflow-x-auto rounded-xl border">
          <Table className="min-w-[420px]">
            <TableHeader>
              <TableRow>
                {["Competitor", "Changes", "Price Drops", "New Products"].map(
                  (h) => (
                    <TableHead key={h} className="px-3.5 text-[10px] font-bold">
                      {h}
                    </TableHead>
                  )
                )}
              </TableRow>
            </TableHeader>
            <TableBody>
              {response.comparisonTable.map((r) => (
                <TableRow key={r.competitor} className="text-[11px] text-muted-foreground">
                  <TableCell className="px-3.5 py-2 text-sm font-medium text-foreground">
                    {r.competitor}
                  </TableCell>
                  <TableCell className="px-3.5 font-medium text-foreground">
                    {r.changes}
                  </TableCell>
                  <TableCell className="px-3.5 font-medium text-success">
                    {r.drops}
                  </TableCell>
                  <TableCell className="px-3.5">{r.newProducts}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {response.chart && (
        <div className="rounded-xl border p-3">
          <p className="mb-2 text-[11px] font-bold text-muted-foreground">
            {response.chart.title}
          </p>
          <ChartContainer config={chartConfig} className="aspect-auto h-[160px] w-full">
            <BarChart data={response.chart.series} margin={{ top: 8, right: 10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fontSize: 10 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10 }} width={28} />
              <ChartTooltip content={<ChartTooltipContent hideLabel />} />
              <Bar
                dataKey="value"
                fill="var(--color-value)"
                radius={[5, 5, 0, 0]}
                barSize={38}
                isAnimationActive={false}
              />
            </BarChart>
          </ChartContainer>
        </div>
      )}

      {response.interpretation && (
        <div className="bg-ai-subtle flex items-start gap-2.5 rounded-xl border border-purple/20 p-3">
          <Badge
            variant="outline"
            className="shrink-0 rounded-full border-purple/25 bg-purple/10 px-2 py-0.5 text-[11px] font-bold text-purple"
          >
            AI interpretation
          </Badge>
          <p className="text-[11px] leading-relaxed text-foreground/70">
            {response.interpretation}
          </p>
        </div>
      )}

      {response.recommendations && (
        <div>
          <p className="mb-1.5 text-xs font-bold">Recommended areas to review</p>
          <ol className="flex flex-col gap-1.5">
            {response.recommendations.map((r, i) => (
              <li key={r} className="flex items-start gap-2 text-xs text-foreground/80">
                <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-accent text-[10px] font-bold text-accent-foreground">
                  {i + 1}
                </span>
                {r}
              </li>
            ))}
          </ol>
        </div>
      )}

      {response.nextStep && (
        <div>
          <p className="text-xs font-bold">Suggested next step</p>
          <p className="mt-1 text-xs text-foreground/80">{response.nextStep}</p>
        </div>
      )}

      {response.caveat && (
        <p className="rounded-xl border border-warning/25 bg-warning/10 p-2.5 text-[11px] leading-relaxed text-foreground/80">
          {response.caveat}
        </p>
      )}

      <div>
        <p className="mb-1.5 text-xs font-bold">Evidence</p>
        <div className="flex flex-wrap gap-1.5">
          {response.evidence.map((e) => (
            <Button
              key={e.label}
              variant="outline"
              size="sm"
              onClick={() => navigate(e.to)}
              className="h-8 rounded-lg text-[11px] font-bold"
            >
              {e.label} <ArrowRight className="size-3" />
            </Button>
          ))}
          {response.actions?.map((a) => {
            const meta = actionMeta[a.kind]
            const Icon = meta.icon
            const act = () => {
              if (a.kind === "alert") {
                navigate("/alerts", {
                  state: { createAlert: a.alertPrefill ?? {} },
                })
              } else if (a.kind === "report") {
                navigate("/reports", {
                  state: { createReport: { typeId: a.reportTypeId ?? null } },
                })
              } else {
                navigate(a.to ?? meta.to)
              }
            }
            return (
              <Button
                key={a.label}
                size="sm"
                onClick={act}
                className="h-8 rounded-lg text-[11px] font-bold"
              >
                <Icon className="size-3.5" /> {a.label}
              </Button>
            )
          })}
        </div>
      </div>

      <p className="flex items-center gap-1 border-t pt-2.5 text-[11px] text-muted-foreground">
        <Clock3 className="size-3" /> Data through {response.dataThrough}
        {response.lastScan && <> · {response.lastScan}</>}
      </p>

      <div className="flex flex-wrap gap-1.5">
        {response.followUps.map((f) => (
          <button
            key={f}
            onClick={() => onFollowUp(f)}
            className="rounded-full border bg-background px-3 py-1.5 text-[11px] font-semibold text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
          >
            {f}
          </button>
        ))}
      </div>
    </div>
  )
}
