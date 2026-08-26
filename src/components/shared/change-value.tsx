import { MoveRight } from "lucide-react"

import { cn } from "@/lib/utils"

/* Old value -> new value evidence, with an optional semantic secondary
   line (e.g. "-16.7%"). */
export function ChangeValue({
  previous,
  current,
  secondary,
  secondaryTone = "muted",
}: {
  previous: string
  current: string
  secondary?: string
  secondaryTone?: "success" | "destructive" | "purple" | "muted"
}) {
  return (
    <span className="inline-flex min-w-0 flex-col gap-0.5">
      <span className="flex min-w-0 flex-wrap items-center gap-1.5">
        <span className="break-words text-muted-foreground line-through decoration-muted-foreground/40">
          {previous}
        </span>
        <MoveRight className="size-3.5 shrink-0 text-muted-foreground/50" />
        <span className="break-words font-medium text-foreground">{current}</span>
      </span>
      {secondary && (
        <span
          className={cn(
            "text-[11px] font-medium",
            secondaryTone === "success" && "text-success",
            secondaryTone === "destructive" && "text-destructive",
            secondaryTone === "purple" && "text-purple",
            secondaryTone === "muted" && "text-muted-foreground"
          )}
        >
          {secondary}
        </span>
      )}
    </span>
  )
}
