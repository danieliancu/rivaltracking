import { monitoringScopeLabels } from "@/lib/settings-data"
import { useWorkspace } from "@/lib/workspace-store"
import { Input } from "@/components/ui/input"
import {
  FormField,
  SettingsSection,
  ToggleRow,
} from "@/components/settings/primitives"

export function MonitoringSection() {
  /* Settings live in the shared workspace store so they survive switching
     between settings sections. Scan frequency is configuration only — the
     actual scheduling happens in the Django/Celery backend. */
  const { settings: workspaceSettings, updateSettings } = useWorkspace()
  const settings = workspaceSettings.monitoring
  const setSettings = (updater: (s: typeof settings) => typeof settings) =>
    updateSettings({ monitoring: updater(settings) })

  return (
    <div className="flex flex-col gap-4">
      <SettingsSection
        title="Monitoring"
        subtitle="Control how often RivalTracking checks monitored competitors."
      >
        <div className="max-w-xs">
          <FormField
            label="Default scan frequency"
            value={settings.frequency}
            onChange={(v) => setSettings((s) => ({ ...s, frequency: v }))}
            options={["Every 24 hours", "Every 12 hours", "Every 6 hours"]}
          />
        </div>
        <ToggleRow
          label="Allow individual competitor schedules"
          description="You can override the default frequency from a competitor's monitoring settings."
          checked={settings.allowOverrides}
          onChange={(c) => setSettings((s) => ({ ...s, allowOverrides: c }))}
        />
        <ToggleRow
          label="Spread scans automatically"
          description="RivalTracking can distribute scans throughout the day to improve reliability and reduce unnecessary load. Recommended."
          checked={settings.spreadScans}
          onChange={(c) => setSettings((s) => ({ ...s, spreadScans: c }))}
        />
      </SettingsSection>

      <SettingsSection
        title="Monitoring scope"
        subtitle="Choose what RivalTracking tracks on competitor product pages."
      >
        {Object.entries(settings.scope).map(([key, on]) => (
          <ToggleRow
            key={key}
            label={monitoringScopeLabels[key]}
            checked={on}
            onChange={(c) =>
              setSettings((s) => ({ ...s, scope: { ...s.scope, [key]: c } }))
            }
          />
        ))}
        <p className="border-t pt-3 text-[11px] font-bold text-muted-foreground">
          Advanced tracking
        </p>
        {Object.entries(settings.advancedScope).map(([key, on]) => (
          <ToggleRow
            key={key}
            label={monitoringScopeLabels[key]}
            checked={on}
            onChange={(c) =>
              setSettings((s) => ({
                ...s,
                advancedScope: { ...s.advancedScope, [key]: c },
              }))
            }
          />
        ))}
      </SettingsSection>

      <SettingsSection
        title="Change detection"
        subtitle="Fine-tune which detected changes are reported."
      >
        <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          Ignore price changes smaller than
          <Input
            value={settings.ignoreThreshold}
            onChange={(e) =>
              setSettings((s) => ({
                ...s,
                ignoreThreshold: e.target.value.replace(/\D/g, ""),
              }))
            }
            className="h-8 w-16 text-center text-xs"
          />
          %
        </div>
        <ToggleRow
          label="Confirm removed products before reporting them"
          description="RivalTracking verifies that temporarily unavailable pages are not incorrectly reported as removed products."
          checked={settings.confirmRemoved}
          onChange={(c) => setSettings((s) => ({ ...s, confirmRemoved: c }))}
        />
      </SettingsSection>

      <SettingsSection title="Monitoring status">
        <div className="grid grid-cols-3 gap-3">
          {[
            ["Competitors monitored", settings.status.competitors],
            ["Default interval", settings.status.interval],
            ["Last monitoring activity", settings.status.lastActivity],
          ].map(([label, value]) => (
            <div key={label}>
              <span className="block text-sm font-medium">{value}</span>
              <span className="mt-0.5 block text-[11px] text-muted-foreground">
                {label}
              </span>
            </div>
          ))}
        </div>
      </SettingsSection>
    </div>
  )
}
