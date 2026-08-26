import { reportTypes, type ReportType } from "@/lib/reports-data"
import { cn } from "@/lib/utils"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function ReportLibrary({
  onSelectType,
}: {
  onSelectType: (type: ReportType) => void
}) {
  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader>
        <CardTitle className="text-sm font-bold">Report Library</CardTitle>
        <CardDescription className="text-xs">
          Generate focused reports from your competitor data.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3.5 md:grid-cols-2 xl:grid-cols-3">
        {reportTypes.map((t) => {
          const Icon = t.icon
          return (
            <button
              key={t.id}
              onClick={() => onSelectType(t)}
              className="flex flex-col gap-2.5 rounded-xl border bg-card p-4 text-left transition-shadow hover:border-primary/30 hover:shadow-md"
            >
              <div className="flex items-center gap-2.5">
                <span
                  className={cn(
                    "flex size-8.5 shrink-0 items-center justify-center rounded-lg",
                    t.tone
                  )}
                >
                  <Icon className="size-4" />
                </span>
                <span className="text-sm font-medium">{t.title}</span>
              </div>
              <p className="text-[11px] leading-relaxed text-muted-foreground">
                {t.description}
              </p>
              <p className="text-[11px] text-muted-foreground/70">
                Includes: {t.includes.join(" · ")}
              </p>
            </button>
          )
        })}
      </CardContent>
    </Card>
  )
}
