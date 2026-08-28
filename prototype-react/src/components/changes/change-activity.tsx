import { useState } from "react"
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts"

import { changeActivity } from "@/lib/changes-data"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

const series = [
  { key: "price", label: "Price", color: "var(--chart-1)" },
  { key: "stock", label: "Stock", color: "var(--warning)" },
  { key: "product", label: "Products", color: "var(--chart-2)" },
  { key: "promotions", label: "Promotions", color: "var(--purple)" },
] as const

const config = Object.fromEntries(
  series.map((s) => [s.key, { label: s.label, color: s.color }])
) satisfies ChartConfig

export function ChangeActivity() {
  const [breakdown, setBreakdown] = useState("all")
  const visible = series.filter((s) => breakdown === "all" || s.key === breakdown)

  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader>
        <CardTitle className="text-sm font-bold">Change Activity</CardTitle>
        <CardDescription className="text-xs">
          Detected changes per hour — spikes reveal competitor campaigns
        </CardDescription>
        <CardAction className="max-md:col-span-2 max-md:col-start-1 max-md:row-start-3 max-md:row-span-1 max-md:mt-1 max-md:justify-self-start">
          <Tabs value={breakdown} onValueChange={setBreakdown}>
            <TabsList className="h-8 rounded-lg">
              <TabsTrigger
                value="all"
                className="rounded-md px-2.5 text-[10px] font-semibold data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
              >
                All
              </TabsTrigger>
              {series.map((s) => (
                <TabsTrigger
                  key={s.key}
                  value={s.key}
                  className="rounded-md px-2.5 text-[10px] font-semibold data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
                >
                  {s.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        </CardAction>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config} className="aspect-auto h-[190px] w-full">
          <LineChart data={changeActivity} margin={{ top: 8, right: 10 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="time"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10 }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10 }}
              width={28}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            {visible.map((s) => (
              <Line
                key={s.key}
                type="monotone"
                dataKey={s.key}
                stroke={`var(--color-${s.key})`}
                strokeWidth={2.5}
                dot={false}
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
