import { useEffect, useRef, useState } from "react"
import { useLocation, useNavigate, useSearchParams } from "react-router-dom"
import { History, Loader2, Plus, Sparkles } from "lucide-react"

import { resolveResponse, type AIResponseData } from "@/lib/ask-ai-data"
import { categoryFromParam } from "@/lib/entities"
import { filterOptions } from "@/lib/products-data"
import { useWorkspace } from "@/lib/workspace-store"
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
import { Card } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { AIComposer } from "@/components/ask-ai/ai-composer"
import { AIContextBar, type AskAIContext } from "@/components/ask-ai/ai-context-bar"
import { AIResponse } from "@/components/ask-ai/ai-response"
import { ConversationHistory } from "@/components/ask-ai/conversation-history"
import { SuggestedQuestions } from "@/components/ask-ai/suggested-questions"

type Message =
  | { id: number; role: "user"; text: string }
  | { id: number; role: "ai"; response: AIResponseData }

const rangePeriods: Record<string, string> = {
  today: "Today",
  "7d": "Last 7 days",
  "30d": "Last 30 days",
}

export function AskAIPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const {
    askAI,
    conversations,
    addConversation,
    renameConversation,
    deleteConversation,
    competitorName,
    products,
  } = useWorkspace()
  const [activeId, setActiveId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [thinking, setThinking] = useState(false)
  const [draft, setDraft] = useState("")
  const [context, setContext] = useState<AskAIContext>({})
  const [historyOpen, setHistoryOpen] = useState(false)
  const [renameId, setRenameId] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState("")
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const endRef = useRef<HTMLDivElement>(null)
  const nextId = useRef(1)

  /* Context handed over from other pages ("Ask AI about these changes"). */
  useEffect(() => {
    const state = location.state as {
      context?: AskAIContext
      prompt?: string
    } | null
    if (!state) return
    if (state.context) setContext(state.context)
    if (state.prompt) setDraft(state.prompt)
    navigate(location.pathname, { replace: true })
  }, [location, navigate])

  /* Deep-link context via ?competitor=&product=&category=&range=&prompt= —
     consumed once into local state, then cleared from the URL. */
  useEffect(() => {
    if ([...searchParams.keys()].length === 0) return
    const next: AskAIContext = {}
    const competitorSlug = searchParams.get("competitor")
    if (competitorSlug) {
      next.competitor = competitorName(competitorSlug) ?? competitorSlug
    }
    const productSlug = searchParams.get("product")
    if (productSlug) {
      next.product =
        products.find((p) => p.slug === productSlug)?.name ?? productSlug
    }
    const categoryToken = searchParams.get("category")
    if (categoryToken) {
      next.category = categoryFromParam(categoryToken, filterOptions.categories)
    }
    const range = searchParams.get("range")
    if (range && rangePeriods[range.toLowerCase()]) {
      next.period = rangePeriods[range.toLowerCase()]
    }
    if (Object.keys(next).length > 0) {
      setContext((prev) => ({ ...prev, ...next }))
    }
    const prompt = searchParams.get("prompt")
    if (prompt) setDraft(prompt.replace(/-/g, " "))
    setSearchParams({}, { replace: true })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" })
  }, [messages, thinking])

  const ask = (question: string) => {
    const q = question.trim()
    if (!q || thinking) return
    setDraft("")
    setMessages((prev) => [...prev, { id: nextId.current++, role: "user", text: q }])
    setThinking(true)
    if (!activeId) {
      /* First message of a fresh conversation creates the history entry. */
      setActiveId(addConversation(q.length > 48 ? `${q.slice(0, 48)}…` : q))
    }
    void askAI(q, context).then((response) => {
      setMessages((prev) => [
        ...prev,
        { id: nextId.current++, role: "ai", response },
      ])
      setThinking(false)
    })
  }

  const newConversation = () => {
    setMessages([])
    setActiveId(null)
    setDraft("")
    setContext({})
  }

  const historyPanel = (
    <ConversationHistory
      conversations={conversations}
      activeId={activeId}
      onOpen={(id) => {
        setActiveId(id)
        setHistoryOpen(false)
        /* Opening a stored conversation replays its topic as a fresh answer. */
        const c = conversations.find((x) => x.id === id)
        if (c) {
          setMessages([
            { id: nextId.current++, role: "user", text: c.title },
            { id: nextId.current++, role: "ai", response: resolveResponse(c.title) },
          ])
        }
      }}
      onDelete={(id) => setDeleteId(id)}
      onRename={(id) => {
        setRenameId(id)
        setRenameValue(conversations.find((c) => c.id === id)?.title ?? "")
      }}
      onNew={newConversation}
    />
  )

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <section className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-2xl font-extrabold tracking-tight">Ask AI</h1>
            <Badge
              variant="outline"
              className="rounded-full border-purple/25 bg-purple/10 px-2 py-0.5 text-[11px] font-bold text-purple"
            >
              Powered by your RivalTracking data
            </Badge>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            Ask questions about your competitors, products and market activity.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setHistoryOpen(true)}
            className="h-9 rounded-lg bg-card text-xs font-bold xl:hidden"
          >
            <History className="size-4" /> History
          </Button>
          <Button
            onClick={newConversation}
            className="h-9 rounded-lg text-xs font-bold shadow-md shadow-primary/25"
          >
            <Plus className="size-4" /> New conversation
          </Button>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-[240px_1fr] xl:items-start">
        <div className="hidden xl:block">{historyPanel}</div>

        <Card className="flex min-h-[calc(100vh-15rem)] flex-col gap-0 rounded-xl p-0 shadow-sm">
          <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-4 sm:p-5">
            {messages.length === 0 && !thinking ? (
              <div className="flex flex-1 flex-col items-center justify-center gap-5 py-8">
                <span className="flex size-12 items-center justify-center rounded-2xl bg-purple/10 text-purple">
                  <Sparkles className="size-6" />
                </span>
                <div className="text-center">
                  <h2 className="text-lg font-bold">
                    What would you like to know?
                  </h2>
                  <p className="mt-1 max-w-sm text-xs text-muted-foreground">
                    Ask RivalTracking about competitor pricing, products, stock,
                    promotions or market activity.
                  </p>
                </div>
                <div className="flex w-full max-w-xl flex-col gap-2.5">
                  {Object.values(context).some(Boolean) && (
                    <AIContextBar context={context} onChange={setContext} />
                  )}
                  <AIComposer
                    value={draft}
                    placeholder="Ask anything about your competitors..."
                    large
                    onChange={setDraft}
                    onSend={() => ask(draft)}
                  />
                </div>
                <SuggestedQuestions onAsk={ask} />
              </div>
            ) : (
              <>
                {messages.map((m) =>
                  m.role === "user" ? (
                    <div key={m.id} className="flex justify-end">
                      <div className="max-w-[85%] rounded-2xl rounded-br-md bg-primary px-3.5 py-2 text-xs font-medium text-primary-foreground sm:max-w-[70%]">
                        {m.text}
                      </div>
                    </div>
                  ) : (
                    <AIResponse key={m.id} response={m.response} onFollowUp={ask} />
                  )
                )}
                {thinking && (
                  <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                    <Loader2 className="size-3.5 animate-spin text-purple" />
                    Analysing competitor data...
                  </div>
                )}
                <div ref={endRef} />
              </>
            )}
          </div>

          {(messages.length > 0 || thinking) && (
            <div className="flex flex-col gap-2.5 border-t p-3.5 sm:p-4">
              <AIContextBar context={context} onChange={setContext} />
              <AIComposer
                value={draft}
                onChange={setDraft}
                onSend={() => ask(draft)}
              />
            </div>
          )}
        </Card>
      </section>

      <Sheet open={historyOpen} onOpenChange={setHistoryOpen}>
        <SheetContent side="left" className="w-72 gap-0 overflow-y-auto p-3">
          <SheetHeader className="p-1 pb-3">
            <SheetTitle className="text-sm font-bold">Conversations</SheetTitle>
          </SheetHeader>
          {historyPanel}
        </SheetContent>
      </Sheet>

      <Dialog open={!!renameId} onOpenChange={(o) => !o && setRenameId(null)}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle className="text-base font-bold">
              Rename conversation
            </DialogTitle>
          </DialogHeader>
          <Input
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && renameId && renameValue.trim()) {
                renameConversation(renameId, renameValue.trim())
                setRenameId(null)
              }
            }}
            aria-label="Conversation name"
            className="h-9 text-xs"
          />
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setRenameId(null)}
              className="h-9 rounded-lg text-xs font-semibold"
            >
              Cancel
            </Button>
            <Button
              disabled={!renameValue.trim()}
              onClick={() => {
                if (renameId) renameConversation(renameId, renameValue.trim())
                setRenameId(null)
              }}
              className="h-9 rounded-lg text-xs font-bold"
            >
              Rename
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteId} onOpenChange={(o) => !o && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-base">
              Delete conversation?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-xs">
              “{conversations.find((c) => c.id === deleteId)?.title}” will be
              permanently removed from your history.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="h-9 text-xs font-semibold">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (deleteId) {
                  deleteConversation(deleteId)
                  if (activeId === deleteId) newConversation()
                }
                setDeleteId(null)
              }}
              className="h-9 bg-destructive text-xs font-bold text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </main>
  )
}
