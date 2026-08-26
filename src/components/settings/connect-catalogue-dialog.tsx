import { Database, FileSpreadsheet, Globe } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

/* Catalogue import runs through the backend Normalizer/Matching services —
   none of these connections work yet, so they are honestly marked. */
const connections = [
  {
    icon: Globe,
    title: "Website",
    description: "CompeteIQ crawls your own catalogue like a competitor's.",
  },
  {
    icon: Database,
    title: "API",
    description: "Push your catalogue directly from your platform.",
  },
  {
    icon: FileSpreadsheet,
    title: "CSV",
    description: "Upload a product export from your store.",
  },
]

export function ConnectCatalogueDialog({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-base font-bold">
            Connect your catalogue
          </DialogTitle>
          <DialogDescription className="text-xs">
            Connecting your own catalogue unlocks direct comparison, pricing
            position and catalogue-gap analysis.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-2.5">
          {connections.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="flex items-center gap-2.5 rounded-xl border p-3 opacity-80"
            >
              <span className="flex size-8.5 shrink-0 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                <Icon className="size-4" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-xs font-bold">{title}</span>
                <span className="mt-0.5 block text-[11px] text-muted-foreground">
                  {description}
                </span>
              </span>
              <Badge
                variant="outline"
                className="rounded-full border-info/25 bg-info/10 px-2 py-0.5 text-[11px] font-bold text-info"
              >
                Coming soon
              </Badge>
            </div>
          ))}
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="h-9 rounded-lg text-xs font-semibold"
          >
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
