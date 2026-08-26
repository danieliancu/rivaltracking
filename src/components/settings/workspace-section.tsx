import { useState } from "react"
import { Link2 } from "lucide-react"
import { toast } from "sonner"

import { workspaceOptions } from "@/lib/settings-data"
import { useWorkspace } from "@/lib/workspace-store"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ConnectCatalogueDialog } from "@/components/settings/connect-catalogue-dialog"
import {
  FormField,
  SaveBar,
  SettingsSection,
} from "@/components/settings/primitives"

export function WorkspaceSection() {
  const { settings, saveSettingsSection } = useWorkspace()
  const [form, setForm] = useState(settings.workspace)
  const [connectOpen, setConnectOpen] = useState(false)
  const dirty = JSON.stringify(settings.workspace) !== JSON.stringify(form)
  const websiteError =
    form.website && !/^https?:\/\/.+\..+/.test(form.website)
      ? "Enter a valid website"
      : undefined

  const set = (key: keyof typeof form) => (value: string) =>
    setForm((f) => ({ ...f, [key]: value }))

  return (
    <div className="flex flex-col gap-4">
      <SettingsSection
        title="Workspace"
        subtitle="Manage your company and market preferences."
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <FormField label="Workspace name" value={form.name} onChange={set("name")} />
          <FormField
            label="Company website"
            value={form.website}
            onChange={set("website")}
            error={websiteError}
          />
          <FormField
            label="Primary market"
            value={form.market}
            onChange={set("market")}
            options={workspaceOptions.markets}
          />
          <FormField
            label="Industry"
            value={form.industry}
            onChange={set("industry")}
            options={workspaceOptions.industries}
          />
          <FormField
            label="Currency"
            value={form.currency}
            onChange={set("currency")}
            options={workspaceOptions.currencies}
          />
          <FormField
            label="Timezone"
            value={form.timezone}
            onChange={set("timezone")}
            options={workspaceOptions.timezones}
          />
          <FormField
            label="Date format"
            value={form.dateFormat}
            onChange={set("dateFormat")}
            options={workspaceOptions.dateFormats}
          />
        </div>
        <SaveBar
          dirty={dirty && !websiteError}
          onCancel={() => setForm(settings.workspace)}
          onSave={() => {
            void saveSettingsSection("workspace", form).then(() =>
              toast.success("Settings saved")
            )
          }}
        />
      </SettingsSection>

      <SettingsSection
        title="Your company data"
        subtitle="Connect your own catalogue for direct comparison, pricing position and catalogue-gap analysis."
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Badge
            variant="outline"
            className="rounded-full border-border bg-muted px-2 py-1 text-[11px] font-bold text-muted-foreground"
          >
            Not connected
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setConnectOpen(true)}
            className="h-8 rounded-lg text-[11px] font-bold"
          >
            <Link2 className="size-3.5" /> Connect your catalogue
          </Button>
        </div>
      </SettingsSection>

      <ConnectCatalogueDialog open={connectOpen} onOpenChange={setConnectOpen} />
    </div>
  )
}
