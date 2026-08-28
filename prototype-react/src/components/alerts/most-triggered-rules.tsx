import { Bar, BarChart, LabelList, XAxis, YAxis } from "recharts"

import { mostTriggeredRules } from "@/lib/alerts-data"
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

const config = {
  count: { label: "Triggered", color: "var(--chart-1)" },
} satisfies ChartConfig

export function MostTriggeredRules() {
  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader>
        <CardTitle className="text-sm font-bold">Most Triggered Rules</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config} className="aspect-auto h-[150px] w-full">
          <BarChart
            data={mostTriggeredRules}
            layout="vertical"
            margin={{ left: 4, right: 30 }}
          >
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="name"
              width={140}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10 }}
            />
            <ChartTooltip content={<ChartTooltipContent hideLabel />} />
            <Bar
              dataKey="count"
              fill="var(--color-count)"
              radius={[0, 5, 5, 0]}
              barSize={14}
              isAnimationActive={false}
            >
              <LabelList
                dataKey="count"
                position="right"
                className="fill-foreground"
                fontSize={10}
                fontWeight={700}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
