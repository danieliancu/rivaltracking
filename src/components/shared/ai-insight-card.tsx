import { type ReactNode } from "react"
import { ArrowRight, Sparkles } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export function AIInsightCard({
  title,
  ctaLabel,
  onCta,
  children,
}: {
  title: string
  ctaLabel: string
  onCta?: () => void
  children: ReactNode
}) {
  return (
    <Card className="bg-ai-subtle gap-4 rounded-2xl border-purple/20 p-5 shadow-sm md:flex-row md:items-start md:gap-3.5">
      <div className="flex min-w-0 flex-1 items-start gap-3.5">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-purple/10 text-purple">
          <Sparkles className="size-5" />
        </div>
        <div className="min-w-0 flex-1">
          <h2 className="text-sm font-bold">{title}</h2>
          <p className="mt-1.5 max-w-4xl text-xs leading-relaxed text-foreground/70">
            {children}
          </p>
        </div>
      </div>
      <Button
        onClick={onCta}
        className="h-9 w-full shrink-0 rounded-lg text-[11px] font-bold md:w-auto md:self-start"
      >
        {ctaLabel} <ArrowRight className="size-3.5" />
      </Button>
    </Card>
  )
}
