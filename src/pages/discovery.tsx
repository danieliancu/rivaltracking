import { useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import {
  Check,
  Compass,
  EllipsisVertical,
  GitCompareArrows,
  Loader2,
  Plus,
  Sparkles,
  Store,
  ThumbsDown,
  X,
} from "lucide-react"
import { toast } from "sonner"

import { discoveryClusters, type DiscoveryCandidate } from "@/lib/discovery-data"
import type { DiscoveryMode } from "@/services/discovery"
import { useWorkspace } from "@/lib/workspace-store"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { CompareCatalogueDrawer } from "@/components/discovery/compare-catalogue-drawer"
import { DiscoveryDialog } from "@/components/discovery/discovery-dialog"
import { WhyMatchDrawer } from "@/components/discovery/why-match-drawer"
import { EmptyState } from "@/components/shared/empty-state"
import { type DiscoveryTone } from "@/components/shared/company-discovery-row"

const toneClasses: Record<DiscoveryTone, string> = {
  blue: "bg-info/10 text-info",
  purple: "bg-purple/10 text-purple",
  teal: "bg-teal/10 text-teal",
  orange: "bg-warning/10 text-warning",
}

export function DiscoveryPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const {
    discoveryCandidates,
    runDiscovery,
    monitorCandidate,
    dismissCandidate,
    markNotRelevant,
  } = useWorkspace()

  const [dialogOpen, setDialogOpen] = useState(false)
  const [whyCandidate, setWhyCandidate] = useState<DiscoveryCandidate | null>(null)
  const [compareCandidate, setCompareCandidate] = useState<DiscoveryCandidate | null>(null)
  const [pending, setPending] = useState<string | null>(null)

  const cluster = searchParams.get("cluster")

  const visible = discoveryCandidates.filter(
    (c) => c.status !== "dismissed" && (!cluster || c.cluster === cluster)
  )

  const setCluster = (id: string | null) => {
    setSearchParams(id ? { cluster: id } : {}, { replace: true })
  }

  const monitor = async (slug: string) => {
    if (pending) return
    const candidate = discoveryCandidates.find((c) => c.slug === slug)
    setPending(slug)
    try {
      await monitorCandidate(slug)
      toast.success("Competitor added", {
        description: `Now monitoring ${candidate?.name ?? slug} — initial snapshot queued.`,
      })
    } finally {
      setPending(null)
    }
  }

  const askAI = (candidate: DiscoveryCandidate) => {
    navigate("/ask-ai", {
      state: {
        context: { competitor: candidate.name, candidate: true },
        prompt: `What do we know about ${candidate.name}?`,
      },
    })
  }

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <section className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">Discovery</h1>
          <p className="mt-1 text-xs text-muted-foreground">
            Find competitors you are not monitoring yet, ranked by catalogue
            similarity.
          </p>
        </div>
        <Button
          onClick={() => setDialogOpen(true)}
          className="h-9 rounded-lg text-xs font-bold shadow-md shadow-primary/25"
        >
          <Compass className="size-4" /> Discover competitors
        </Button>
      </section>

      <section className="grid grid-cols-1 gap-3.5 sm:grid-cols-3">
        {discoveryClusters.map((c) => {
          const count = discoveryCandidates.filter(
            (x) => x.cluster === c.id && x.status !== "dismissed"
          ).length
          const active = cluster === c.id
          return (
            <Card
              key={c.id}
              role="button"
              tabIndex={0}
              aria-label={`Filter by ${c.label}`}
              onClick={() => setCluster(active ? null : c.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault()
                  setCluster(active ? null : c.id)
                }
              }}
              className={cn(
                "cursor-pointer gap-0 rounded-xl p-4 shadow-sm transition-shadow hover:shadow-md",
                active && "border-primary/40 bg-accent/40"
              )}
            >
              <span className="block text-sm font-bold">{c.label}</span>
              <span className="mt-0.5 block text-[11px] font-semibold text-muted-foreground">
                {count} potential {count === 1 ? "competitor" : "competitors"}
              </span>
            </Card>
          )
        })}
      </section>

      <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-sm font-bold">Discovery results</CardTitle>
          <CardDescription className="text-xs">
            {cluster ? (
              <span className="flex items-center gap-2">
                Filtered to {cluster}
                <button
                  onClick={() => setCluster(null)}
                  aria-label="Clear cluster filter"
                  className="inline-flex items-center gap-0.5 text-[11px] font-bold text-primary"
                >
                  <X className="size-3" /> Clear
                </button>
              </span>
            ) : (
              "Companies similar to your monitored competitors."
            )}
          </CardDescription>
        </CardHeader>

        {visible.length === 0 ? (
          <EmptyState
            icon={Compass}
            heading="No discoveries yet"
            text="Run discovery to find companies with overlapping catalogues."
            actionLabel="Discover competitors"
            onAction={() => setDialogOpen(true)}
          />
        ) : (
          visible.map((d) => (
            <div key={d.slug} className="flex items-center gap-2.5 border-t px-5 py-3">
              <span
                className={cn(
                  "flex size-8.5 shrink-0 items-center justify-center rounded-lg",
                  toneClasses[d.tone as DiscoveryTone] ?? toneClasses.blue
                )}
              >
                <Store className="size-4" />
              </span>
              <button
                onClick={() => setWhyCandidate(d)}
                className="min-w-0 flex-1 text-left"
                aria-label={`Why is ${d.name} a match?`}
              >
                <span className="block truncate text-sm font-medium hover:text-primary">
                  {d.name}
                </span>
                <span className="mt-0.5 block text-[11px] text-muted-foreground">
                  {d.match}% match · {d.cluster}
                </span>
              </button>
              <Badge
                variant="outline"
                onClick={() => setWhyCandidate(d)}
                className="hidden cursor-pointer rounded-full border-info/25 bg-info/10 px-2 py-0.5 text-[11px] font-bold text-info sm:inline-flex"
              >
                {d.catalogueProfile.overlap}
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={() => monitor(d.slug)}
                disabled={pending === d.slug || d.status === "monitoring"}
                className={cn(
                  "h-7 rounded-lg px-2.5 text-[11px] font-bold",
                  d.status === "monitoring" &&
                    "border-success/30 bg-success/10 text-success disabled:opacity-100"
                )}
              >
                {pending === d.slug ? (
                  <Loader2 className="size-3.5 animate-spin" />
                ) : d.status === "monitoring" ? (
                  <Check className="size-3.5" />
                ) : (
                  <Plus className="size-3.5" />
                )}
                {pending === d.slug
                  ? "Monitoring…"
                  : d.status === "monitoring"
                    ? "Monitoring"
                    : "Monitor"}
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`More actions for ${d.name}`}
                    className="size-7 rounded-lg text-muted-foreground"
                  >
                    <EllipsisVertical className="size-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuItem onClick={() => setWhyCandidate(d)}>
                    <Compass className="size-3.5" /> Why this match?
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setCompareCandidate(d)}>
                    <GitCompareArrows className="size-3.5" /> Compare with ToyWorld
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => askAI(d)}>
                    <Sparkles className="size-3.5" /> Ask AI about this company
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={async () => {
                      await markNotRelevant(d.slug)
                      toast.info("Feedback saved", {
                        description: `${d.name} will no longer be suggested.`,
                      })
                    }}
                  >
                    <ThumbsDown className="size-3.5" /> Not relevant
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={async () => {
                      await dismissCandidate(d.slug)
                      toast.info("Suggestion dismissed")
                    }}
                  >
                    <X className="size-3.5" /> Dismiss
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ))
        )}
      </Card>

      <DiscoveryDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onRun={async (mode: DiscoveryMode, input: string) => {
          const found = await runDiscovery(mode, input)
          toast.success("Discovery complete", {
            description:
              found > 0
                ? `${found} ${found === 1 ? "suggestion" : "suggestions"} refreshed.`
                : "No new candidates found — existing suggestions are up to date.",
          })
        }}
      />
      <WhyMatchDrawer
        candidate={whyCandidate}
        onClose={() => setWhyCandidate(null)}
        onMonitor={monitor}
      />
      <CompareCatalogueDrawer
        candidate={compareCandidate}
        onClose={() => setCompareCandidate(null)}
      />
    </main>
  )
}
