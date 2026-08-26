import { CalendarClock, CheckCircle2, Clock3, TriangleAlert } from "lucide-react"

import { monitoringHealth } from "@/lib/competitors-data"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const stats = [
  {
    icon: CheckCircle2,
    tone: "text-success",
    value: `${monitoringHealth.healthy} competitors`,
    label: "Healthy",
  },
  {
    icon: TriangleAlert,
    tone: "text-warning",
    value: `${monitoringHealth.attention} competitor`,
    label: "Needs attention",
  },
  {
    icon: Clock3,
    tone: "text-info",
    value: monitoringHealth.lastSuccessfulScan,
    label: "Last successful scan",
  },
  {
    icon: CalendarClock,
    tone: "text-purple",
    value: monitoringHealth.nextScheduledScan,
    label: "Next scheduled scan",
  },
]

export function MonitoringHealth() {
  const total = monitoringHealth.healthy + monitoringHealth.attention
  const healthyShare = (monitoringHealth.healthy / total) * 100

  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader>
        <CardTitle className="text-sm font-bold">Monitoring Health</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-x-3 gap-y-4 md:grid-cols-4">
          {stats.map(({ icon: Icon, tone, value, label }) => (
            <div key={label} className="flex items-start gap-2">
              <Icon className={`mt-0.5 size-4 shrink-0 ${tone}`} />
              <span>
                <span className="block text-xs font-bold">{value}</span>
                <span className="mt-0.5 block text-[10px] text-muted-foreground">
                  {label}
                </span>
              </span>
            </div>
          ))}
        </div>
        <div>
          <div className="flex h-2 w-full gap-1 overflow-hidden rounded-full">
            <div
              className="rounded-full bg-success"
              style={{ width: `${healthyShare}%` }}
            />
            <div className="flex-1 rounded-full bg-warning" />
          </div>
          <p className="mt-2 text-[10px] text-muted-foreground">
            {monitoringHealth.healthy} of {total} competitors are scanning
            without issues.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
