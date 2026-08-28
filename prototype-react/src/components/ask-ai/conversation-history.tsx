import { MoreHorizontal, Pencil, Plus, Trash2 } from "lucide-react"

import { type conversationHistory } from "@/lib/ask-ai-data"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

type Conversation = (typeof conversationHistory)[number]

export function ConversationHistory({
  conversations,
  activeId,
  onOpen,
  onDelete,
  onRename,
  onNew,
}: {
  conversations: Conversation[]
  activeId: string | null
  onOpen: (id: string) => void
  onDelete: (id: string) => void
  onRename: (id: string) => void
  onNew: () => void
}) {
  return (
    <Card className="gap-0 overflow-hidden rounded-xl pb-0 shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-bold">Conversations</CardTitle>
      </CardHeader>
      {conversations.map((c) => (
        // div instead of button: the row contains its own action menu button,
        // and buttons cannot nest.
        <div
          key={c.id}
          role="button"
          tabIndex={0}
          onClick={() => onOpen(c.id)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault()
              onOpen(c.id)
            }
          }}
          className={cn(
            "group flex w-full cursor-pointer items-center gap-1.5 border-t px-4 py-2.5 text-left hover:bg-muted/50",
            activeId === c.id && "bg-accent/60"
          )}
        >
          <span className="min-w-0 flex-1">
            <span className="block truncate text-sm font-medium">{c.title}</span>
            <span className="mt-0.5 block text-[11px] text-muted-foreground">
              {c.when}
            </span>
          </span>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="size-6 shrink-0 text-muted-foreground opacity-0 group-hover:opacity-100"
                onClick={(e) => e.stopPropagation()}
              >
                <MoreHorizontal className="size-3.5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
              <DropdownMenuItem onClick={() => onOpen(c.id)}>Open</DropdownMenuItem>
              <DropdownMenuItem onClick={() => onRename(c.id)}>
                <Pencil className="size-3.5" /> Rename
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                variant="destructive"
                onClick={() => onDelete(c.id)}
              >
                <Trash2 className="size-3.5" /> Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      ))}
      <div className="border-t p-0">
        <Button
          variant="ghost"
          onClick={onNew}
          className="h-10 w-full rounded-none text-[11px] font-bold text-primary"
        >
          <Plus className="size-3.5" /> New conversation
        </Button>
      </div>
    </Card>
  )
}
