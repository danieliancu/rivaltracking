import { ChevronDown } from "lucide-react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  Line,
  LineChart,
  Pie,
  PieChart,
  XAxis,
  YAxis,
} from "recharts"

import { overviewByRange, ranges, type RangeKey } from "@/lib/data"
import { useUiState } from "@/lib/ui-store"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

const trendConfig = {
  median: { label: "Median Price", color: "var(--chart-1)" },
  average: { label: "Average Price", color: "var(--chart-2)" },
} satisfies ChartConfig

const categoriesConfig = {
  value: { label: "Share", color: "var(--chart-1)" },
} satisfies ChartConfig

const stockColors: Record<string, string> = {
  "In Stock": "var(--success)",
  "Out of Stock": "var(--warning)",
  "Back in Stock": "var(--chart-1)",
}

const stockConfig = {
  value: { label: "Products" },
} satisfies ChartConfig

const rangeLabels: Record<RangeKey, string> = {
  today: "Today",
  "7d": "Last 7 days",
  "30d": "Last 30 days",
}

export function AnalyticsCharts() {
  const { dateRange, setDateRange } = useUiState()
  const { priceTrend, categories, stock, totalProducts } = overviewByRange[dateRange]

  return (
    <section className="grid gap-4 lg:grid-cols-2 2xl:grid-cols-[2fr_1fr_1fr]">
      <Card className="rounded-xl shadow-sm lg:col-span-2 2xl:col-span-1">
        <CardHeader className="items-start">
          <CardTitle className="text-sm font-bold">Price Change Trend</CardTitle>
          <CardDescription className="flex gap-3.5 text-[10px]">
            <span className="flex items-center gap-1.5">
              <i className="size-1.5 rounded-full bg-chart-1" /> Median Price
            </span>
            <span className="flex items-center gap-1.5">
              <i className="size-1.5 rounded-full bg-chart-2" /> Average Price
            </span>
          </CardDescription>
          <CardAction>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 text-[10px] font-semibold text-muted-foreground"
                >
                  {rangeLabels[dateRange]} <ChevronDown className="size-3.5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {ranges.map((r) => (
                  <DropdownMenuItem
                    key={r.key}
                    onClick={() => setDateRange(r.key)}
                    className="text-xs font-semibold"
                  >
                    {rangeLabels[r.key]}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </CardAction>
        </CardHeader>
        <CardContent>
          <ChartContainer config={trendConfig} className="aspect-auto h-[245px] w-full">
            <LineChart data={priceTrend} margin={{ top: 10, right: 10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="date"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />
              <YAxis
                domain={[-10, 10]}
                ticks={[-10, -5, 0, 5, 10]}
                tickFormatter={(v) => `${v}%`}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
                width={40}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line
                type="monotone"
                dataKey="median"
                stroke="var(--color-median)"
                strokeWidth={2.5}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="average"
                stroke="var(--color-average)"
                strokeWidth={2.5}
                strokeDasharray="6 4"
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>

      <Card className="rounded-xl shadow-sm">
        <CardHeader>
          <CardTitle className="text-sm font-bold">
            Top Moving Categories
          </CardTitle>
          <CardDescription className="text-xs">
            Share of detected price movements
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={categoriesConfig}
            className="aspect-auto h-[245px] w-full"
          >
            <BarChart
              data={categories}
              layout="vertical"
              margin={{ left: 4, right: 34 }}
            >
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis
                type="category"
                dataKey="name"
                width={112}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />
              <ChartTooltip content={<ChartTooltipContent hideLabel />} />
              <Bar
                dataKey="value"
                fill="var(--color-value)"
                radius={[0, 5, 5, 0]}
                barSize={18}
                isAnimationActive={false}
              >
                <LabelList
                  dataKey="value"
                  position="right"
                  formatter={(v: unknown) => `${v}%`}
                  className="fill-foreground"
                  fontSize={10}
                  fontWeight={700}
                />
              </Bar>
            </BarChart>
          </ChartContainer>
        </CardContent>
      </Card>

      <Card className="rounded-xl shadow-sm">
        <CardHeader>
          <CardTitle className="text-sm font-bold">Stock Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative mx-auto h-[170px] w-[190px]">
            <ChartContainer config={stockConfig} className="aspect-auto h-full w-full">
              <PieChart>
                <Pie
                  data={stock}
                  dataKey="value"
                  nameKey="name"
                  innerRadius="70%"
                  outerRadius="95%"
                  paddingAngle={3}
                  strokeWidth={0}
                  isAnimationActive={false}
                >
                  {stock.map((s) => (
                    <Cell key={s.name} fill={stockColors[s.name]} />
                  ))}
                </Pie>
                <ChartTooltip content={<ChartTooltipContent hideLabel />} />
              </PieChart>
            </ChartContainer>
            <div className="pointer-events-none absolute inset-0 grid place-content-center text-center">
              <span className="text-[21px] font-bold">{totalProducts}</span>
              <span className="mt-0.5 text-[10px] text-muted-foreground">
                Total
              </span>
            </div>
          </div>
          <div className="mt-3 flex flex-col gap-2">
            {stock.map((s) => (
              <div
                key={s.name}
                className="grid grid-cols-[1fr_auto_45px] items-center gap-2 text-[10px]"
              >
                <span className="flex items-center gap-2 text-muted-foreground">
                  <i
                    className="size-2 rounded-full"
                    style={{ background: stockColors[s.name] }}
                  />
                  {s.name}
                </span>
                <span className="font-bold">{s.value.toLocaleString()}</span>
                <span className="text-right text-muted-foreground">
                  {s.percent}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </section>
  )
}
