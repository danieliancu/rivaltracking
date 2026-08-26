import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts"

import { priceMovement } from "@/lib/products-data"
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

const config = {
  decreases: { label: "Price decreases", color: "var(--success)" },
  increases: { label: "Price increases", color: "var(--destructive)" },
} satisfies ChartConfig

export function PriceMovement() {
  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader>
        <CardTitle className="text-sm font-bold">Price Movement</CardTitle>
        <CardDescription className="flex gap-3.5 text-[10px]">
          <span className="flex items-center gap-1.5">
            <i className="size-1.5 rounded-full bg-success" />
            Price decreases:{" "}
            <strong className="text-success">{priceMovement.decreases}</strong>
          </span>
          <span className="flex items-center gap-1.5">
            <i className="size-1.5 rounded-full bg-destructive" />
            Price increases:{" "}
            <strong className="text-destructive">
              {priceMovement.increases}
            </strong>
          </span>
        </CardDescription>
        <CardAction className="text-[10px] font-semibold text-muted-foreground">
          Last 30 days
        </CardAction>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config} className="aspect-auto h-[180px] w-full">
          <LineChart data={priceMovement.series} margin={{ top: 8, right: 10 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10 }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10 }}
              width={30}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Line
              type="monotone"
              dataKey="decreases"
              stroke="var(--color-decreases)"
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="increases"
              stroke="var(--color-increases)"
              strokeWidth={2.5}
              strokeDasharray="6 4"
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
