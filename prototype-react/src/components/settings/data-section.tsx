import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Download, ShieldCheck, Trash2 } from "lucide-react"
import { toast } from "sonner"

import { dataSettings } from "@/lib/settings-data"
import { downloadJson } from "@/lib/csv"
import { useWorkspace } from "@/lib/workspace-store"
import { Button } from "@/components/ui/button"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Input } from "@/components/ui/input"
import {
  FormField,
  SettingsSection,
} from "@/components/settings/primitives"

export function DataSection() {
  const navigate = useNavigate()
  const {
    settings,
    updateSettings,
    competitors,
    exportWorkspaceSnapshot,
    deleteCompetitorData,
    deleteWorkspace,
  } = useWorkspace()
  const workspaceName = settings.workspace.name
  const retention = settings.retention
  const setRetention = (value: string) => updateSettings({ retention: value })
  const competitorNames =
    competitors.length > 0
      ? competitors.map((c) => c.name)
      : dataSettings.competitors
  const [deleteCompetitorOpen, setDeleteCompetitorOpen] = useState(false)
  const [competitorToDelete, setCompetitorToDelete] = useState(competitorNames[0])
  const [deleteWorkspaceOpen, setDeleteWorkspaceOpen] = useState(false)
  const [confirmPhrase, setConfirmPhrase] = useState("")

  const exportData = () => {
    downloadJson("rivaltracking-workspace.json", exportWorkspaceSnapshot())
    toast.success("Export ready", {
      description: "Workspace data downloaded as JSON.",
    })
  }

  return (
    <div className="flex flex-col gap-4">
      <SettingsSection
        title="Data & Privacy"
        subtitle="Manage your RivalTracking data and retention preferences."
      >
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {dataSettings.stats.map((s) => (
            <div key={s.label}>
              <span className="block text-sm font-medium">{s.value}</span>
              <span className="mt-0.5 block text-[11px] text-muted-foreground">
                {s.label}
              </span>
            </div>
          ))}
        </div>
        <div className="max-w-xs border-t pt-4">
          <FormField
            label="Historical data retention"
            value={retention}
            onChange={setRetention}
            options={dataSettings.retentionOptions}
          />
        </div>
      </SettingsSection>

      <SettingsSection
        title="Export workspace data"
        subtitle="Export your stored competitor intelligence in a portable format."
      >
        <Button
          variant="outline"
          size="sm"
          onClick={exportData}
          className="h-8 w-fit rounded-lg text-[11px] font-bold"
        >
          <Download className="size-3.5" /> Export data
        </Button>
      </SettingsSection>

      <SettingsSection title="Competitor monitoring">
        <p className="flex items-start gap-2 text-[11px] leading-relaxed text-muted-foreground">
          <ShieldCheck className="mt-0.5 size-3.5 shrink-0 text-success" />
          RivalTracking is designed to monitor information available from publicly
          accessible competitor pages and configured data sources.
        </p>
      </SettingsSection>

      <SettingsSection
        title="Danger zone"
        subtitle="These actions are permanent and cannot be undone."
      >
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-destructive/25 p-3.5">
          <div>
            <span className="block text-xs font-bold">Delete competitor data</span>
            <span className="mt-0.5 block text-[11px] text-muted-foreground">
              This permanently removes historical monitoring data for selected
              competitors.
            </span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setDeleteCompetitorOpen(true)}
            className="h-8 rounded-lg border-destructive/30 text-[11px] font-bold text-destructive hover:bg-destructive/10 hover:text-destructive"
          >
            <Trash2 className="size-3.5" /> Delete competitor data
          </Button>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-destructive/25 p-3.5">
          <div>
            <span className="block text-xs font-bold">Delete workspace</span>
            <span className="mt-0.5 block text-[11px] text-muted-foreground">
              Permanently deletes this workspace, its competitors, history,
              reports and team access.
            </span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setDeleteWorkspaceOpen(true)}
            className="h-8 rounded-lg border-destructive/30 text-[11px] font-bold text-destructive hover:bg-destructive/10 hover:text-destructive"
          >
            <Trash2 className="size-3.5" /> Delete workspace
          </Button>
        </div>
      </SettingsSection>

      <AlertDialog
        open={deleteCompetitorOpen}
        onOpenChange={setDeleteCompetitorOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-base">
              Delete competitor data?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-xs">
              This permanently removes all historical monitoring data for the
              selected competitor. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <FormField
            label="Competitor"
            value={competitorToDelete}
            onChange={setCompetitorToDelete}
            options={competitorNames}
          />
          <AlertDialogFooter>
            <AlertDialogCancel className="h-9 text-xs font-semibold">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={async () => {
                await deleteCompetitorData(competitorToDelete)
                toast.info("Competitor data deleted", {
                  description: `Historical data for ${competitorToDelete} was removed.`,
                })
              }}
              className="h-9 bg-destructive text-xs font-bold text-destructive-foreground hover:bg-destructive/90"
            >
              Delete data
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog
        open={deleteWorkspaceOpen}
        onOpenChange={(o) => {
          setDeleteWorkspaceOpen(o)
          if (!o) setConfirmPhrase("")
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-base">
              Delete this workspace?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-xs">
              This action is permanent. Type{" "}
              <strong className="text-foreground">{workspaceName}</strong> to
              confirm.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <Input
            value={confirmPhrase}
            onChange={(e) => setConfirmPhrase(e.target.value)}
            placeholder={workspaceName}
            className="h-9 text-xs"
          />
          <AlertDialogFooter>
            <AlertDialogCancel className="h-9 text-xs font-semibold">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              disabled={confirmPhrase !== workspaceName}
              onClick={async () => {
                await deleteWorkspace()
                toast.info("Workspace deleted", {
                  description: "All workspace data was removed.",
                })
                navigate("/")
              }}
              className="h-9 bg-destructive text-xs font-bold text-destructive-foreground hover:bg-destructive/90"
            >
              Delete workspace
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
