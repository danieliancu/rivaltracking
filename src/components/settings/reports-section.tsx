import { reportDetailOptions } from "@/lib/settings-data"
import { useWorkspace } from "@/lib/workspace-store"
import {
  FormField,
  RadioCards,
  SettingsSection,
  ToggleRow,
} from "@/components/settings/primitives"

export function ReportsSection() {
  const { settings: workspaceSettings, updateSettings } = useWorkspace()
  const settings = workspaceSettings.reports
  const setSettings = (updater: (s: typeof settings) => typeof settings) =>
    updateSettings({ reports: updater(settings) })

  return (
    <div className="flex flex-col gap-4">
      <SettingsSection
        title="Reports"
        subtitle="Set defaults for generated intelligence reports."
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <FormField
            label="Default report period"
            value={settings.period}
            onChange={(v) => setSettings((s) => ({ ...s, period: v }))}
            options={["Today", "Last 7 days", "Last 30 days"]}
          />
          <FormField
            label="Default competitors"
            value={settings.competitors}
            onChange={(v) => setSettings((s) => ({ ...s, competitors: v }))}
            options={[
              "All monitored competitors",
              "ToyWorld.co.uk",
              "PlayNest.co.uk",
              "HappyToyHouse.com",
              "LittleMindsToys.co.uk",
            ]}
          />
        </div>
        <ToggleRow
          label="Include AI analysis by default"
          checked={settings.aiByDefault}
          onChange={(c) => setSettings((s) => ({ ...s, aiByDefault: c }))}
        />
      </SettingsSection>

      <SettingsSection title="Report detail">
        <RadioCards
          options={reportDetailOptions}
          value={settings.detail}
          onChange={(v) => setSettings((s) => ({ ...s, detail: v }))}
        />
      </SettingsSection>

      <SettingsSection
        title="Report branding"
        subtitle="Shown on exported PDF reports."
      >
        <div className="max-w-xs">
          <FormField
            label="Company name"
            value={settings.brandingName}
            onChange={(v) => setSettings((s) => ({ ...s, brandingName: v }))}
          />
        </div>
        <p className="text-[11px] text-muted-foreground">
          Logo upload — coming later.
        </p>
      </SettingsSection>

      <SettingsSection
        title="Scheduled report defaults"
        subtitle="Used when scheduling new reports."
      >
        <div className="grid max-w-md grid-cols-3 gap-2">
          <FormField
            label="Daily intelligence"
            value={settings.dailyTime}
            onChange={(v) => setSettings((s) => ({ ...s, dailyTime: v }))}
            options={["06:00", "08:00", "12:00"]}
          />
          <FormField
            label="Weekly intelligence"
            value={settings.weeklyDay}
            onChange={(v) => setSettings((s) => ({ ...s, weeklyDay: v }))}
            options={["Monday", "Friday"]}
          />
          <FormField
            label="Time"
            value={settings.weeklyTime}
            onChange={(v) => setSettings((s) => ({ ...s, weeklyTime: v }))}
            options={["06:00", "08:00", "16:00"]}
          />
        </div>
      </SettingsSection>
    </div>
  )
}
