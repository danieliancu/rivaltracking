import { useState } from "react"
import { Mail, MoreHorizontal, Trash2, UserCog, UserPlus } from "lucide-react"
import { toast } from "sonner"

import { roleDescriptions, type TeamMember } from "@/lib/settings-data"
import * as settingsService from "@/services/settings"
import { useWorkspace } from "@/lib/workspace-store"
import { cn } from "@/lib/utils"
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
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { FormField, SettingsSection } from "@/components/settings/primitives"

const assignableRoles: TeamMember["role"][] = ["Admin", "Analyst", "Viewer"]

export function TeamSection() {
  const { settings, updateSettings } = useWorkspace()
  const members = settings.team
  const setMembers = (next: TeamMember[]) => updateSettings({ team: next })
  const [inviteOpen, setInviteOpen] = useState(false)
  const [inviteEmail, setInviteEmail] = useState("")
  const [inviteRole, setInviteRole] = useState("Analyst")
  const [toRemove, setToRemove] = useState<TeamMember | null>(null)

  const invite = async () => {
    await settingsService.inviteMember(inviteEmail, inviteRole)
    setMembers([
      ...members,
      {
        id: `m-${inviteEmail}`,
        name: inviteEmail.split("@")[0],
        email: inviteEmail,
        role: inviteRole as TeamMember["role"],
        status: "Invited",
        lastActive: "—",
      },
    ])
    toast.success("Invitation sent", { description: inviteEmail })
    setInviteEmail("")
    setInviteOpen(false)
  }

  const changeRole = (member: TeamMember, role: TeamMember["role"]) => {
    setMembers(members.map((m) => (m.id === member.id ? { ...m, role } : m)))
    toast.success("Role updated", { description: `${member.name} is now ${role}.` })
  }

  const resendInvite = (member: TeamMember) => {
    toast.success("Invitation resent", { description: member.email })
  }

  return (
    <div className="flex flex-col gap-4">
      <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-sm font-bold">Team</CardTitle>
          <CardDescription className="text-xs">
            Manage who can access this CompeteIQ workspace.
          </CardDescription>
          <CardAction>
            <Button
              size="sm"
              onClick={() => setInviteOpen(true)}
              className="h-8 rounded-lg text-[11px] font-bold"
            >
              <UserPlus className="size-3.5" /> Invite member
            </Button>
          </CardAction>
        </CardHeader>
        <CardContent className="px-0 pb-0">
          <div className="overflow-x-auto">
            <Table className="min-w-[640px]">
              <TableHeader>
                <TableRow>
                  {["Name", "Email", "Role", "Status", "Last Active", ""].map(
                    (h, i) => (
                      <TableHead key={i} className="px-3.5 text-[10px] font-bold">
                        {h}
                      </TableHead>
                    )
                  )}
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.map((m) => (
                  <TableRow key={m.id} className="text-[11px] text-muted-foreground">
                    <TableCell className="px-3.5 py-2.5">
                      <span className="flex items-center gap-2.5">
                        <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-accent text-[11px] font-bold text-accent-foreground">
                          {m.name
                            .split(/[\s.]/)
                            .filter(Boolean)
                            .slice(0, 2)
                            .map((p) => p[0]?.toUpperCase())
                            .join("")}
                        </span>
                        <span className="text-sm font-medium text-foreground">
                          {m.name}
                        </span>
                      </span>
                    </TableCell>
                    <TableCell className="px-3.5">{m.email}</TableCell>
                    <TableCell className="px-3.5">
                      <Badge
                        variant="secondary"
                        className="rounded-full text-[11px] font-bold text-muted-foreground"
                      >
                        {m.role}
                      </Badge>
                    </TableCell>
                    <TableCell className="px-3.5">
                      <Badge
                        variant="outline"
                        className={cn(
                          "gap-1.5 rounded-full px-2 py-1 text-[11px] font-bold",
                          m.status === "Active"
                            ? "border-success/25 bg-success/10 text-success"
                            : "border-info/25 bg-info/10 text-info"
                        )}
                      >
                        <i
                          className={cn(
                            "size-1.5 rounded-full",
                            m.status === "Active" ? "bg-success" : "bg-info"
                          )}
                        />
                        {m.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="px-3.5">{m.lastActive}</TableCell>
                    <TableCell className="px-2 text-right">
                      {m.role !== "Owner" && (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              aria-label={`Actions for ${m.name}`}
                              className="size-7 text-muted-foreground"
                            >
                              <MoreHorizontal className="size-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuSub>
                              <DropdownMenuSubTrigger>
                                <UserCog className="mr-1.5 size-3.5" /> Change role
                              </DropdownMenuSubTrigger>
                              <DropdownMenuSubContent>
                                {assignableRoles.map((role) => (
                                  <DropdownMenuItem
                                    key={role}
                                    disabled={role === m.role}
                                    onClick={() => changeRole(m, role)}
                                  >
                                    {role}
                                  </DropdownMenuItem>
                                ))}
                              </DropdownMenuSubContent>
                            </DropdownMenuSub>
                            {m.status === "Invited" && (
                              <DropdownMenuItem onClick={() => resendInvite(m)}>
                                <Mail className="size-3.5" /> Resend invitation
                              </DropdownMenuItem>
                            )}
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              variant="destructive"
                              onClick={() => setToRemove(m)}
                            >
                              <Trash2 className="size-3.5" /> Remove
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <SettingsSection title="Roles">
        <div className="grid gap-3 sm:grid-cols-2">
          {roleDescriptions.map((r) => (
            <div key={r.role}>
              <span className="block text-xs font-bold">{r.role}</span>
              <span className="mt-0.5 block text-[11px] text-muted-foreground">
                {r.description}
              </span>
            </div>
          ))}
        </div>
      </SettingsSection>

      <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle className="text-base font-bold">
              Invite member
            </DialogTitle>
            <DialogDescription className="text-xs">
              They will receive an invitation to join this workspace.
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-3.5">
            <FormField
              label="Email"
              value={inviteEmail}
              onChange={setInviteEmail}
              placeholder="colleague@company.com"
            />
            <FormField
              label="Role"
              value={inviteRole}
              onChange={setInviteRole}
              options={["Admin", "Analyst", "Viewer"]}
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setInviteOpen(false)}
              className="h-9 rounded-lg text-xs font-semibold"
            >
              Cancel
            </Button>
            <Button
              onClick={invite}
              disabled={!/.+@.+\..+/.test(inviteEmail)}
              className="h-9 rounded-lg text-xs font-bold"
            >
              Send invitation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!toRemove} onOpenChange={(o) => !o && setToRemove(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-base">
              Remove {toRemove?.name}?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-xs">
              {toRemove?.email} will lose access to this workspace immediately.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="h-9 text-xs font-semibold">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (toRemove) {
                  setMembers(members.filter((x) => x.id !== toRemove.id))
                  toast.info("Member removed", { description: toRemove.email })
                }
                setToRemove(null)
              }}
              className="h-9 bg-destructive text-xs font-bold text-destructive-foreground hover:bg-destructive/90"
            >
              Remove member
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
