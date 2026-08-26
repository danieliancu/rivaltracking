import { ArrowRight } from "lucide-react"

import { changePatterns, type ChangePattern } from "@/lib/changes-data"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export function ChangePatterns({
  onApplyPattern,
}: {
  onApplyPattern: (pattern: ChangePattern) => void
}) {
  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-sm font-bold">Major Change Patterns</h2>
      <div className="grid gap-3.5 md:grid-cols-3">
        {changePatterns.map((p) => {
          const Icon = p.icon
          return (
            <Card key={p.id} className="gap-3 rounded-xl p-4 shadow-sm">
              <div className="flex items-center gap-2.5">
                <span
                  className={cn(
                    "flex size-8.5 shrink-0 items-center justify-center rounded-lg",
                    p.tone
                  )}
                >
                  <Icon className="size-4" />
                </span>
                <span className="min-w-0">
                  <span className="block truncate text-sm font-medium">
                    {p.title}
                  </span>
                  <span className="mt-0.5 block text-[11px] text-muted-foreground">
                    {p.competitor}
                  </span>
                </span>
              </div>
              <div>
                <span className="block text-lg font-bold tracking-tight">
                  {p.stat}
                </span>
                <span className="mt-0.5 block text-[11px] text-muted-foreground">
                  {p.statDetail} · {p.meta}
                </span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onApplyPattern(p)}
                className="h-8 w-fit rounded-lg text-[11px] font-bold"
              >
                {p.cta} <ArrowRight className="size-3.5" />
              </Button>
            </Card>
          )
        })}
      </div>
    </section>
  )
}
