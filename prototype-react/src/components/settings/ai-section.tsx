import { aiStyleOptions } from "@/lib/settings-data"
import { useWorkspace } from "@/lib/workspace-store"
import {
  RadioCards,
  SettingsSection,
  ToggleRow,
} from "@/components/settings/primitives"

export function AISection() {
  const { settings: workspaceSettings, updateSettings } = useWorkspace()
  const settings = workspaceSettings.ai
  const setSettings = (updater: (s: typeof settings) => typeof settings) =>
    updateSettings({ ai: updater(settings) })

  return (
    <div className="flex flex-col gap-4">
      <SettingsSection
        title="AI"
        subtitle="Control how AI-assisted intelligence is presented."
      >
        <ToggleRow
          label="AI analysis"
          description="Allow RivalTracking to interpret verified competitor data and highlight patterns, risks and opportunities."
          checked={settings.aiAnalysis}
          onChange={(c) => setSettings((s) => ({ ...s, aiAnalysis: c }))}
        />
        <ToggleRow
          label="Include AI analysis in reports by default"
          checked={settings.aiInReports}
          onChange={(c) => setSettings((s) => ({ ...s, aiInReports: c }))}
        />
        <ToggleRow
          label="Add AI explanation to important alerts"
          description="Alerts are always triggered by your rules and verified data — AI only explains why they may matter."
          checked={settings.aiInAlerts}
          onChange={(c) => setSettings((s) => ({ ...s, aiInAlerts: c }))}
        />
      </SettingsSection>

      <SettingsSection title="AI recommendations">
        <RadioCards
          options={aiStyleOptions}
          value={settings.style}
          onChange={(v) => setSettings((s) => ({ ...s, style: v }))}
        />
        <ToggleRow
          label="Show supporting evidence with AI insights"
          description="AI insights link back to RivalTracking's verified changes, products and analytics wherever possible."
          checked={settings.showEvidence}
          onChange={(c) => setSettings((s) => ({ ...s, showEvidence: c }))}
        />
      </SettingsSection>

      <SettingsSection title="AI data usage">
        <p className="text-[11px] leading-relaxed text-muted-foreground">
          RivalTracking sends only the relevant structured context needed to answer
          your request rather than your entire competitor database.
        </p>
        <p className="border-t pt-3 text-[11px] leading-relaxed text-muted-foreground">
          RivalTracking AI interprets collected competitive data. Strategic
          interpretations may be uncertain and should be reviewed alongside
          supporting evidence.
        </p>
      </SettingsSection>
    </div>
  )
}
