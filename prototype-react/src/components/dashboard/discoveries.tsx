import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowRight } from "lucide-react"
import { toast } from "sonner"

import { useWorkspace } from "@/lib/workspace-store"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  CompanyDiscoveryRow,
  type DiscoveryTone,
} from "@/components/shared/company-discovery-row"
import { EmptyState } from "@/components/shared/empty-state"

export function Discoveries() {
  const navigate = useNavigate()
  const { discoveryCandidates, monitorCandidate } = useWorkspace()
  const [pending, setPending] = useState<string | null>(null)

  const suggestions = discoveryCandidates
    .filter((c) => c.status !== "dismissed")
    .slice(0, 4)

  const monitor = async (slug: string, name: string) => {
    if (pending) return
    setPending(slug)
    try {
      await monitorCandidate(slug)
      toast.success("Competitor added", {
        description: `Now monitoring ${name} — initial snapshot queued.`,
      })
    } finally {
      setPending(null)
    }
  }

  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-bold">
          Similar Companies Discovered
        </CardTitle>
        <CardDescription className="text-xs">
          Auto-detected competitors matching your market
        </CardDescription>
      </CardHeader>
      {suggestions.length === 0 ? (
        <EmptyState
          heading="No discoveries yet"
          text="Run discovery to find companies similar to your competitors."
          actionLabel="Discover competitors"
          onAction={() => navigate("/discovery")}
        />
      ) : (
        suggestions.map((d) => (
          <CompanyDiscoveryRow
            key={d.slug}
            name={d.name}
            match={d.match}
            tone={d.tone as DiscoveryTone}
            monitoring={d.status === "monitoring"}
            pending={pending === d.slug}
            onToggle={() => monitor(d.slug, d.name)}
          />
        ))
      )}
      <CardFooter className="border-t p-0">
        <Button
          variant="ghost"
          onClick={() => navigate("/discovery")}
          className="h-11 w-full rounded-none text-[11px] font-bold text-primary"
        >
          View all discoveries <ArrowRight className="size-3.5" />
        </Button>
      </CardFooter>
    </Card>
  )
}
