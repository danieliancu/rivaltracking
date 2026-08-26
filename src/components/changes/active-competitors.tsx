import { Bar, BarChart, LabelList, XAxis, YAxis } from "recharts"

import { competitorActivity } from "@/lib/changes-data"
import {
  Card,
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

const config = {
  changes: { label: "Changes", color: "var(--chart-1)" },
} satisfies ChartConfig

export function ActiveCompetitors() {
  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader>
        <CardTitle className="text-sm font-bold">Most Active Competitors</CardTitle>
        <CardDescription className="text-xs">
          Detected changes per competitor today
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config} className="aspect-auto h-[190px] w-full">
          <BarChart
            data={competitorActivity}
            layout="vertical"
            margin={{ left: 4, right: 34 }}
          >
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="name"
              width={132}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11 }}
            />
            <ChartTooltip content={<ChartTooltipContent hideLabel />} />
            <Bar
              dataKey="changes"
              fill="var(--color-changes)"
              radius={[0, 5, 5, 0]}
              barSize={18}
              isAnimationActive={false}
            >
              <LabelList
                dataKey="changes"
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
