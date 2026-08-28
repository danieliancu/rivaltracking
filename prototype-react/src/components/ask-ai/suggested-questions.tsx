import { ArrowRight } from "lucide-react"

import { activitySuggestions, suggestedQuestions } from "@/lib/ask-ai-data"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Zap } from "lucide-react"

export function SuggestedQuestions({ onAsk }: { onAsk: (q: string) => void }) {
  return (
    <div className="flex w-full max-w-2xl flex-col gap-5">
      <div className="flex flex-wrap justify-center gap-1.5">
        {suggestedQuestions.map((s) => (
          <button
            key={s.question}
            onClick={() => onAsk(s.question)}
            className="rounded-full border bg-card px-3 py-1.5 text-[11px] font-semibold text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
          >
            <span className="mr-1.5 text-primary">{s.category}</span>
            {s.question}
          </button>
        ))}
      </div>

      <div>
        <p className="mb-2 text-center text-[11px] font-bold text-muted-foreground">
          Suggested from today's activity
        </p>
        <div className="grid gap-2.5 sm:grid-cols-3">
          {activitySuggestions.map((a) => (
            <div key={a.title} className="rounded-xl border bg-card p-3">
              <div className="flex items-center gap-2">
                <span
                  className={cn(
                    "flex size-7 shrink-0 items-center justify-center rounded-lg",
                    a.tone
                  )}
                >
                  <Zap className="size-3.5" />
                </span>
                <span className="truncate text-xs font-bold">{a.title}</span>
              </div>
              <p className="mt-1.5 text-[11px] text-muted-foreground">{a.detail}</p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onAsk(a.prompt)}
                className="mt-1 h-7 rounded-lg px-1.5 text-[11px] font-bold text-primary"
              >
                {a.cta} <ArrowRight className="size-3" />
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
