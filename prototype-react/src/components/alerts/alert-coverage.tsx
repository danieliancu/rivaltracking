import { Bell, Boxes, FolderSearch, TriangleAlert } from "lucide-react"

import { alertCoverage } from "@/lib/alerts-data"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const icons = [Bell, Boxes, FolderSearch, TriangleAlert]
const tones = ["text-info", "text-teal", "text-purple", "text-warning"]

export function AlertCoverage() {
  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader>
        <CardTitle className="text-sm font-bold">Alert Coverage</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-x-3 gap-y-4">
        {alertCoverage.map((s, i) => {
          const Icon = icons[i]
          return (
            <div key={s.label} className="flex items-start gap-2">
              <Icon className={`mt-0.5 size-4 shrink-0 ${tones[i]}`} />
              <span>
                <span className="block text-sm font-medium">{s.value}</span>
                <span className="mt-0.5 block text-[11px] text-muted-foreground">
                  {s.label}
                </span>
              </span>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
