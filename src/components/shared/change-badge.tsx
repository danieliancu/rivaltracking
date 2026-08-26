import {
  BadgePercent,
  CircleHelp,
  FileText,
  FolderPen,
  Layers,
  PackageCheck,
  PackageX,
  Pencil,
  Sparkles,
  Trash2,
  TrendingDown,
  TrendingUp,
  type LucideIcon,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

export type ChangeKind =
  | "drop"
  | "increase"
  | "promo"
  | "promo-end"
  | "oos"
  | "back"
  | "new"
  | "removed"
  | "missing"
  | "name"
  | "category"
  | "description"
  | "variant-add"
  | "variant-remove"

const kindMeta: Record<ChangeKind, { icon: LucideIcon; classes: string }> = {
  drop: {
    icon: TrendingDown,
    classes: "border-success/25 bg-success/10 text-success",
  },
  increase: {
    icon: TrendingUp,
    classes: "border-destructive/25 bg-destructive/10 text-destructive",
  },
  promo: {
    icon: BadgePercent,
    classes: "border-purple/25 bg-purple/10 text-purple",
  },
  oos: {
    icon: PackageX,
    classes: "border-warning/25 bg-warning/10 text-warning",
  },
  back: {
    icon: PackageCheck,
    classes: "border-success/25 bg-success/10 text-success",
  },
  new: {
    icon: Sparkles,
    classes: "border-info/25 bg-info/10 text-info",
  },
  removed: {
    icon: Trash2,
    classes: "border-destructive/25 bg-destructive/10 text-destructive",
  },
  name: {
    icon: Pencil,
    classes: "border-border bg-muted text-muted-foreground",
  },
  category: {
    icon: FolderPen,
    classes: "border-border bg-muted text-muted-foreground",
  },
  "promo-end": {
    icon: BadgePercent,
    classes: "border-border bg-muted text-muted-foreground",
  },
  missing: {
    icon: CircleHelp,
    classes: "border-warning/25 bg-warning/10 text-warning",
  },
  description: {
    icon: FileText,
    classes: "border-border bg-muted text-muted-foreground",
  },
  "variant-add": {
    icon: Layers,
    classes: "border-teal/25 bg-teal/10 text-teal",
  },
  "variant-remove": {
    icon: Layers,
    classes: "border-border bg-muted text-muted-foreground",
  },
}

export function ChangeBadge({
  kind,
  label,
}: {
  kind: ChangeKind
  label: string
}) {
  const meta = kindMeta[kind]
  const Icon = meta.icon
  return (
    <Badge
      variant="outline"
      className={cn(
        "gap-1.5 rounded-full px-2 py-1 text-[11px] font-bold",
        meta.classes
      )}
    >
      <Icon className="size-3" />
      {label}
    </Badge>
  )
}
