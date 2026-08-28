import { Store } from "lucide-react"

import { cn } from "@/lib/utils"

const tones = [
  "bg-info/10 text-info",
  "bg-purple/10 text-purple",
  "bg-teal/10 text-teal",
  "bg-warning/10 text-warning",
  "bg-rose/10 text-rose",
]

/* Deterministic tone per company name so identity colors stay stable. */
function toneFor(name: string) {
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) | 0
  return tones[Math.abs(hash) % tones.length]
}

export function CompetitorIdentity({
  name,
  url,
}: {
  name: string
  url?: string
}) {
  return (
    <div className="flex items-center gap-2.5">
      <span
        className={cn(
          "flex size-8.5 shrink-0 items-center justify-center rounded-full",
          toneFor(name)
        )}
      >
        <Store className="size-4" />
      </span>
      <span className="min-w-0">
        <span className="block truncate text-sm font-medium text-foreground">
          {name}
        </span>
        {url && (
          <span className="mt-0.5 block truncate text-[11px] text-muted-foreground">
            {url}
          </span>
        )}
      </span>
    </div>
  )
}
