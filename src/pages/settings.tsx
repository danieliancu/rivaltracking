import { useNavigate, useParams } from "react-router-dom"
import {
  Bell,
  Building2,
  CreditCard,
  Database,
  FileBarChart2,
  Radar,
  Sparkles,
  Users,
  type LucideIcon,
} from "lucide-react"

import { settingsSections, type SettingsSectionId } from "@/lib/settings-data"
import { cn } from "@/lib/utils"
import { Card } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { AISection } from "@/components/settings/ai-section"
import { BillingSection } from "@/components/settings/billing-section"
import { DataSection } from "@/components/settings/data-section"
import { MonitoringSection } from "@/components/settings/monitoring-section"
import { NotificationsSection } from "@/components/settings/notifications-section"
import { ReportsSection } from "@/components/settings/reports-section"
import { TeamSection } from "@/components/settings/team-section"
import { WorkspaceSection } from "@/components/settings/workspace-section"

const sectionIcons: Record<SettingsSectionId, LucideIcon> = {
  workspace: Building2,
  monitoring: Radar,
  notifications: Bell,
  ai: Sparkles,
  reports: FileBarChart2,
  team: Users,
  data: Database,
  billing: CreditCard,
}

const sectionComponents: Record<SettingsSectionId, () => React.ReactNode> = {
  workspace: () => <WorkspaceSection />,
  monitoring: () => <MonitoringSection />,
  notifications: () => <NotificationsSection />,
  ai: () => <AISection />,
  reports: () => <ReportsSection />,
  team: () => <TeamSection />,
  data: () => <DataSection />,
  billing: () => <BillingSection />,
}

export function SettingsPage() {
  const { section } = useParams()
  const navigate = useNavigate()
  const active: SettingsSectionId = settingsSections.some((s) => s.id === section)
    ? (section as SettingsSectionId)
    : "workspace"

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <section>
        <h1 className="text-2xl font-extrabold tracking-tight">Settings</h1>
        <p className="mt-1 text-xs text-muted-foreground">
          Configure how CompeteIQ works for your company.
        </p>
      </section>

      {/* Section picker on smaller screens */}
      <div className="xl:hidden">
        <Select
          value={active}
          onValueChange={(v) => navigate(`/settings/${v}`)}
        >
          <SelectTrigger className="h-9 w-56 text-xs font-semibold">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {settingsSections.map((s) => (
              <SelectItem key={s.id} value={s.id} className="text-xs">
                {s.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <section className="grid gap-4 xl:grid-cols-[220px_1fr] xl:items-start">
        <Card className="hidden gap-0 overflow-hidden rounded-xl py-2 shadow-sm xl:block">
          {settingsSections.map((s) => {
            const Icon = sectionIcons[s.id]
            return (
              <button
                key={s.id}
                onClick={() => navigate(`/settings/${s.id}`)}
                className={cn(
                  "flex w-full items-center gap-2.5 px-4 py-2.5 text-left text-[13px] font-semibold transition-colors",
                  active === s.id
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
              >
                <Icon className="size-4" />
                {s.label}
              </button>
            )
          })}
        </Card>

        <div className="min-w-0">{sectionComponents[active]()}</div>
      </section>
    </main>
  )
}
