import { useNavigate } from "react-router-dom"
import {
  BadgePercent,
  PackageX,
  Sparkles,
  TrendingDown,
  TriangleAlert,
  type LucideIcon,
} from "lucide-react"

import { activityEvents, type ActivityEvent } from "@/lib/competitors-data"
import { slugForCompetitor } from "@/lib/entities"
import { cn } from "@/lib/utils"
import { Card, CardHeader, CardTitle } from "@/components/ui/card"

const kindMeta: Record<ActivityEvent["kind"], { icon: LucideIcon; tone: string }> = {
  "prices-down": { icon: TrendingDown, tone: "bg-success/10 text-success" },
  "new-products": { icon: Sparkles, tone: "bg-info/10 text-info" },
  "pages-unavailable": { icon: TriangleAlert, tone: "bg-warning/10 text-warning" },
  "out-of-stock": { icon: PackageX, tone: "bg-destructive/10 text-destructive" },
  promotion: { icon: BadgePercent, tone: "bg-purple/10 text-purple" },
}

/* Each activity kind deep-links to the most relevant area of the app. */
function routeFor(event: ActivityEvent): string {
  const slug = slugForCompetitor(event.company)
  switch (event.kind) {
    case "prices-down":
      return `/changes?type=price-decrease&competitor=${slug}`
    case "new-products":
      return `/products?change=new&competitor=${slug}`
    case "pages-unavailable":
      return `/competitors/${slug}`
    case "out-of-stock":
      return `/changes?type=out-of-stock&competitor=${slug}`
    case "promotion":
      return `/changes?type=promotion-started&competitor=${slug}`
  }
}

export function RecentActivity() {
  const navigate = useNavigate()
  return (
    <Card className="gap-0 rounded-xl pb-0 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-bold">
          Recent Competitor Activity
        </CardTitle>
      </CardHeader>
      {activityEvents.map((e, i) => {
        const meta = kindMeta[e.kind]
        const Icon = meta.icon
        return (
          <button
            key={i}
            onClick={() => navigate(routeFor(e))}
            className="flex w-full items-center gap-2.5 border-t px-5 py-3 text-left transition-colors hover:bg-accent/40"
          >
            <span
              className={cn(
                "flex size-8.5 shrink-0 items-center justify-center rounded-lg",
                meta.tone
              )}
            >
              <Icon className="size-4" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-medium">
                {e.company}
              </span>
              <span className="mt-0.5 block truncate text-[11px] text-muted-foreground">
                {e.event}
              </span>
            </span>
            <span className="shrink-0 text-[11px] text-muted-foreground">
              {e.time}
            </span>
          </button>
        )
      })}
    </Card>
  )
}
