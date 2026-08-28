import { Slack } from "lucide-react"

import { emailOptionLabels } from "@/lib/settings-data"
import { useWorkspace } from "@/lib/workspace-store"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  FormField,
  SettingsSection,
  ToggleRow,
} from "@/components/settings/primitives"

export function NotificationsSection() {
  const { settings: workspaceSettings, updateSettings } = useWorkspace()
  const settings = workspaceSettings.notifications
  const setSettings = (updater: (s: typeof settings) => typeof settings) =>
    updateSettings({ notifications: updater(settings) })

  return (
    <div className="flex flex-col gap-4">
      <SettingsSection
        title="Notifications"
        subtitle="Choose how RivalTracking keeps you informed."
      >
        <ToggleRow
          label="In-app notifications"
          checked={settings.inApp}
          onChange={(c) => setSettings((s) => ({ ...s, inApp: c }))}
        />
        {settings.inApp && (
          <div className="flex flex-col gap-3 border-l-2 border-border pl-4">
            {(["high", "medium", "low"] as const).map((p) => (
              <ToggleRow
                key={p}
                label={`${p[0].toUpperCase() + p.slice(1)} priority`}
                checked={settings.priorities[p]}
                onChange={(c) =>
                  setSettings((s) => ({
                    ...s,
                    priorities: { ...s.priorities, [p]: c },
                  }))
                }
              />
            ))}
          </div>
        )}
      </SettingsSection>

      <SettingsSection title="Email notifications">
        <ToggleRow
          label="Email notifications"
          checked={settings.email}
          onChange={(c) => setSettings((s) => ({ ...s, email: c }))}
        />
        {settings.email && (
          <div className="flex flex-col gap-3 border-l-2 border-border pl-4">
            <div className="max-w-xs">
              <FormField
                label="Email"
                value={settings.emailAddress}
                onChange={(v) => setSettings((s) => ({ ...s, emailAddress: v }))}
              />
            </div>
            {Object.entries(settings.emailOptions).map(([key, on]) => (
              <ToggleRow
                key={key}
                label={emailOptionLabels[key]}
                checked={on}
                onChange={(c) =>
                  setSettings((s) => ({
                    ...s,
                    emailOptions: { ...s.emailOptions, [key]: c },
                  }))
                }
              />
            ))}
            <div className="grid max-w-md grid-cols-3 gap-2">
              <FormField
                label="Daily digest"
                value={settings.digestTime}
                onChange={(v) => setSettings((s) => ({ ...s, digestTime: v }))}
                options={["06:00", "08:00", "12:00", "18:00"]}
              />
              <FormField
                label="Weekly report"
                value={settings.weeklyDay}
                onChange={(v) => setSettings((s) => ({ ...s, weeklyDay: v }))}
                options={["Monday", "Friday", "Sunday"]}
              />
              <FormField
                label="Time"
                value={settings.weeklyTime}
                onChange={(v) => setSettings((s) => ({ ...s, weeklyTime: v }))}
                options={["06:00", "08:00", "12:00", "18:00"]}
              />
            </div>
            <p className="text-[11px] text-muted-foreground">
              Times use your workspace timezone (Europe/London).
            </p>
          </div>
        )}
      </SettingsSection>

      <SettingsSection title="Slack">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="flex items-center gap-2">
            <Badge
              variant="outline"
              className="rounded-full border-border bg-muted px-2 py-1 text-[11px] font-bold text-muted-foreground"
            >
              Not connected
            </Badge>
            <Badge
              variant="outline"
              className="rounded-full border-info/25 bg-info/10 px-2 py-1 text-[11px] font-bold text-info"
            >
              Coming soon
            </Badge>
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled
            className="h-8 rounded-lg text-[11px] font-bold"
          >
            <Slack className="size-3.5" /> Connect Slack
          </Button>
        </div>
      </SettingsSection>
    </div>
  )
}
