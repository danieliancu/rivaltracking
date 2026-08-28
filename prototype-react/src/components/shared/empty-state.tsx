import { type LucideIcon, SearchX } from "lucide-react"

import { Button } from "@/components/ui/button"

export function EmptyState({
  icon: Icon = SearchX,
  heading,
  text,
  actionLabel,
  onAction,
}: {
  icon?: LucideIcon
  heading: string
  text: string
  actionLabel?: string
  onAction?: () => void
}) {
  return (
    <div className="flex flex-col items-center gap-1.5 px-6 py-12 text-center">
      <Icon className="mb-1 size-8 text-muted-foreground/40" />
      <p className="text-sm font-bold">{heading}</p>
      <p className="max-w-xs text-xs text-muted-foreground">{text}</p>
      {actionLabel && (
        <Button
          onClick={onAction}
          className="mt-3 h-9 rounded-lg text-xs font-bold"
        >
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
