import { useNavigate } from "react-router-dom"
import {
  Package,
  PackageX,
  Percent,
  Sparkles,
  TrendingDown,
  TrendingUp,
  type LucideIcon,
} from "lucide-react"

import { kpis as defaultKpis, type OverviewDataset } from "@/lib/data"
import { KpiCard, type KpiTone } from "@/components/shared/kpi-card"

const iconByKpi: Record<string, LucideIcon> = {
  monitored: Package,
  new: Sparkles,
  reductions: TrendingDown,
  increases: TrendingUp,
  oos: PackageX,
  promos: Percent,
}

/* Each KPI deep-links into the list view pre-filtered to what it counts. */
const routeByKpi: Record<string, string> = {
  monitored: "/products",
  new: "/products?change=new",
  reductions: "/changes?type=price-decrease",
  increases: "/changes?type=price-increase",
  oos: "/products?stock=out",
  promos: "/changes?type=promotion-started",
}

export function KpiCards({ kpis = defaultKpis }: { kpis?: OverviewDataset["kpis"] }) {
  const navigate = useNavigate()
  return (
    <section className="grid grid-cols-2 gap-3.5 md:grid-cols-3 xl:grid-cols-6">
      {kpis.map(([id, label, value, tone]) => (
        <KpiCard
          key={id}
          icon={iconByKpi[id]}
          tone={tone as KpiTone}
          value={value}
          label={label}
          onClick={routeByKpi[id] ? () => navigate(routeByKpi[id]) : undefined}
        />
      ))}
    </section>
  )
}
