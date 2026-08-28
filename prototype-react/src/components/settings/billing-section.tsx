import { useState } from "react"
import { CreditCard } from "lucide-react"

import { billing } from "@/lib/settings-data"
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
import { SettingsSection, UsageBar } from "@/components/settings/primitives"

export function BillingSection() {
  const [manageOpen, setManageOpen] = useState(false)
  return (
    <div className="flex flex-col gap-4">
      <SettingsSection
        title="Billing"
        subtitle="Manage your RivalTracking plan and usage."
      >
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border p-3.5">
          <div className="flex items-center gap-2.5">
            <span className="flex size-8.5 items-center justify-center rounded-lg bg-info/10 text-info">
              <CreditCard className="size-4" />
            </span>
            <span>
              <span className="flex items-center gap-2 text-sm font-medium">
                {billing.plan}
                <Badge
                  variant="outline"
                  className="gap-1.5 rounded-full border-success/25 bg-success/10 px-2 py-0.5 text-[11px] font-bold text-success"
                >
                  <i className="size-1.5 rounded-full bg-success" />
                  {billing.status}
                </Badge>
              </span>
              <span className="mt-0.5 block text-[11px] text-muted-foreground">
                Current plan
              </span>
            </span>
          </div>
          <Button
            onClick={() => setManageOpen(true)}
            className="h-9 rounded-lg text-xs font-bold shadow-md shadow-primary/25"
          >
            Manage plan
          </Button>
        </div>
      </SettingsSection>

      <SettingsSection title="Usage">
        {billing.usage.map((u) => (
          <UsageBar
            key={u.label}
            label={u.label}
            display={u.display}
            used={u.used}
            limit={u.limit}
          />
        ))}
        <div className="grid grid-cols-2 gap-3 border-t pt-4">
          {billing.facts.map((f) => (
            <div key={f.label}>
              <span className="block text-sm font-medium">{f.value}</span>
              <span className="mt-0.5 block text-[11px] text-muted-foreground">
                {f.label}
              </span>
            </div>
          ))}
        </div>
        <p className="text-[11px] text-muted-foreground">
          Plan limits are enforced by RivalTracking when adding competitors or
          increasing scan frequency.
        </p>
      </SettingsSection>

      <Dialog open={manageOpen} onOpenChange={setManageOpen}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle className="text-base font-bold">Manage plan</DialogTitle>
            <DialogDescription className="text-xs">
              Billing backend is not connected yet. Plan changes, invoices and
              payment methods will be handled here once billing is integrated.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setManageOpen(false)}
              className="h-9 rounded-lg text-xs font-semibold"
            >
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
