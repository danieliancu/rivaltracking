import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react"

import * as aiService from "@/services/ai"
import * as competitorService from "@/services/competitors"
import * as discoveryService from "@/services/discovery"
import * as productService from "@/services/products"
import * as reportService from "@/services/reports"
import * as settingsService from "@/services/settings"
import { competitorRows, type CompetitorRow } from "@/lib/competitors-data"
import { changeEventsResponse, type ChangeEvent } from "@/lib/changes-data"
import { conversationHistory } from "@/lib/ask-ai-data"
import {
  discoveryCandidatesSeed,
  type DiscoveryCandidate,
} from "@/lib/discovery-data"
import { generatedReports, reportSchedules as scheduleSeed, type GeneratedReport, type ReportSchedule } from "@/lib/reports-data"
import { productsResponse, type ProductRow } from "@/lib/products-data"
import {
  aiSettings,
  monitoringSettings,
  notificationSettings,
  reportSettings,
  teamMembers,
  workspaceSettings,
  type TeamMember,
} from "@/lib/settings-data"
import { slugify } from "@/lib/entities"
import { useUiState } from "@/lib/ui-store"

/*
 * Central mock application state. Components never call services directly —
 * they call the async actions here, which call the (mocked) service layer
 * and then update state. When the Django REST API exists, only the services
 * change; components and this store's interface stay the same.
 *
 * The watchlist is a visual bookmark on products. Watch notifications are
 * NOT a separate engine — "watch product" flows create an AlertRule through
 * the existing Create Alert dialog, so the Alert Engine stays the single
 * notification pipeline.
 */

export type Conversation = { id: string; title: string; when: string }

export type WorkspaceSettingsState = {
  workspace: typeof workspaceSettings
  monitoring: typeof monitoringSettings
  notifications: typeof notificationSettings
  ai: typeof aiSettings
  reports: typeof reportSettings
  team: TeamMember[]
  retention: string
}

const defaultCompetitorConfig: competitorService.CompetitorMonitoringConfig = {
  frequency: "Every 24 hours",
  trackPrices: true,
  trackStock: true,
  trackProducts: true,
  trackPromotions: true,
}

const initialSettings = (): WorkspaceSettingsState => ({
  workspace: { ...workspaceSettings },
  monitoring: structuredClone(monitoringSettings),
  notifications: structuredClone(notificationSettings),
  ai: { ...aiSettings },
  reports: { ...reportSettings },
  team: [...teamMembers],
  retention: "12 months",
})

type WorkspaceContextValue = {
  competitors: CompetitorRow[]
  products: ProductRow[]
  changeEvents: ChangeEvent[]
  reports: GeneratedReport[]
  reportSchedules: ReportSchedule[]
  discoveryCandidates: DiscoveryCandidate[]
  watchlist: ReadonlySet<string>
  conversations: Conversation[]
  settings: WorkspaceSettingsState
  competitorConfigs: Record<string, competitorService.CompetitorMonitoringConfig>
  getCompetitorConfig: (slug: string) => competitorService.CompetitorMonitoringConfig
  competitorName: (slug: string) => string | undefined
  competitorSlug: (name: string) => string

  runScan: (competitorName: string) => Promise<competitorService.ScanResult>
  addCompetitor: (url: string) => Promise<CompetitorRow>
  monitorCandidate: (slug: string) => Promise<CompetitorRow | null>
  pauseCompetitor: (slug: string) => Promise<void>
  resumeCompetitor: (slug: string) => Promise<void>
  removeCompetitor: (slug: string) => Promise<void>
  saveCompetitorConfig: (
    slug: string,
    config: competitorService.CompetitorMonitoringConfig
  ) => Promise<void>

  toggleWatchlist: (slug: string) => boolean
  addToWatchlist: (slugs: string[]) => Promise<number>

  createReport: (input: reportService.ReportInput) => Promise<GeneratedReport>
  deleteReport: (id: string) => Promise<void>
  saveSchedule: (schedule: ReportSchedule) => Promise<void>
  toggleSchedule: (id: string) => void
  deleteSchedule: (id: string) => Promise<void>

  runDiscovery: (mode: discoveryService.DiscoveryMode, input: string) => Promise<number>
  dismissCandidate: (slug: string) => Promise<void>
  markNotRelevant: (slug: string) => Promise<void>

  askAI: typeof aiService.askAI
  addConversation: (title: string) => string
  renameConversation: (id: string, title: string) => void
  deleteConversation: (id: string) => void

  updateSettings: (patch: Partial<WorkspaceSettingsState>) => void
  saveSettingsSection: <K extends keyof WorkspaceSettingsState>(
    section: K,
    values: WorkspaceSettingsState[K]
  ) => Promise<void>
  exportWorkspaceSnapshot: () => Record<string, unknown>
  deleteCompetitorData: (name: string) => Promise<void>
  deleteWorkspace: () => Promise<void>
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null)

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { setScanning } = useUiState()

  const [competitors, setCompetitors] = useState<CompetitorRow[]>(competitorRows)
  const [products, setProducts] = useState<ProductRow[]>(productsResponse.results)
  const [changeEvents, setChangeEvents] = useState<ChangeEvent[]>(
    changeEventsResponse.results
  )
  const [reports, setReports] = useState<GeneratedReport[]>(generatedReports)
  const [reportSchedules, setReportSchedules] = useState<ReportSchedule[]>(scheduleSeed)
  const [discoveryCandidates, setDiscoveryCandidates] = useState<DiscoveryCandidate[]>(
    discoveryCandidatesSeed
  )
  const [watchlist, setWatchlist] = useState<Set<string>>(new Set())
  const [conversations, setConversations] = useState<Conversation[]>(conversationHistory)
  const [settings, setSettings] = useState<WorkspaceSettingsState>(initialSettings)
  const [competitorConfigs, setCompetitorConfigs] = useState<
    Record<string, competitorService.CompetitorMonitoringConfig>
  >({})
  const conversationCounter = useRef(100)

  const runScan = useCallback(
    async (name: string) => {
      setScanning(true)
      try {
        const result = await competitorService.runScan(name)
        setCompetitors((prev) =>
          prev.map((c) =>
            name === "All competitors" || c.name === name
              ? { ...c, lastScan: "Just now" }
              : c
          )
        )
        return result
      } finally {
        setScanning(false)
      }
    },
    [setScanning]
  )

  const addCompetitor = useCallback(async (url: string) => {
    const row = await competitorService.addCompetitor(url)
    setCompetitors((prev) =>
      prev.some((c) => c.slug === row.slug) ? prev : [...prev, row]
    )
    return row
  }, [])

  const monitorCandidate = useCallback(
    async (slug: string) => {
      const candidate = discoveryCandidates.find((c) => c.slug === slug)
      if (!candidate) return null
      setDiscoveryCandidates((prev) =>
        prev.map((c) => (c.slug === slug ? { ...c, status: "monitoring" } : c))
      )
      const row = await competitorService.addCompetitor(candidate.url)
      const finalRow: CompetitorRow = {
        ...row,
        slug: candidate.slug,
        name: candidate.name,
        url: candidate.url,
        products: candidate.catalogueProfile.products,
      }
      setCompetitors((prev) =>
        prev.some((c) => c.slug === finalRow.slug) ? prev : [...prev, finalRow]
      )
      return finalRow
    },
    [discoveryCandidates]
  )

  const pauseCompetitor = useCallback(async (slug: string) => {
    await competitorService.pauseCompetitor(slug)
    setCompetitors((prev) =>
      prev.map((c) => (c.slug === slug ? { ...c, status: "paused" } : c))
    )
  }, [])

  const resumeCompetitor = useCallback(async (slug: string) => {
    await competitorService.resumeCompetitor(slug)
    setCompetitors((prev) =>
      prev.map((c) => (c.slug === slug ? { ...c, status: "healthy" } : c))
    )
  }, [])

  const removeCompetitor = useCallback(async (slug: string) => {
    await competitorService.removeCompetitor(slug)
    setCompetitors((prev) => prev.filter((c) => c.slug !== slug))
  }, [])

  const saveCompetitorConfig = useCallback(
    async (slug: string, config: competitorService.CompetitorMonitoringConfig) => {
      await competitorService.saveMonitoringConfig(slug, config)
      setCompetitorConfigs((prev) => ({ ...prev, [slug]: config }))
    },
    []
  )

  const toggleWatchlist = useCallback(
    (slug: string) => {
      const added = !watchlist.has(slug)
      setWatchlist((prev) => {
        const next = new Set(prev)
        if (next.has(slug)) next.delete(slug)
        else next.add(slug)
        return next
      })
      if (added) void productService.addToWatchlist([slug])
      else void productService.removeFromWatchlist(slug)
      return added
    },
    [watchlist]
  )

  const addToWatchlist = useCallback(
    async (slugs: string[]) => {
      const fresh = slugs.filter((slug) => !watchlist.has(slug))
      setWatchlist((prev) => new Set([...prev, ...fresh]))
      await productService.addToWatchlist(fresh)
      return fresh.length
    },
    [watchlist]
  )

  const createReport = useCallback(async (input: reportService.ReportInput) => {
    const id = `${input.typeId}-${Date.now().toString(36)}`
    const report = await reportService.generateReport(input, id)
    setReports((prev) => [report, ...prev])
    return report
  }, [])

  const deleteReport = useCallback(async (id: string) => {
    await reportService.deleteReport(id)
    setReports((prev) => prev.filter((r) => r.id !== id))
  }, [])

  const saveSchedule = useCallback(async (schedule: ReportSchedule) => {
    await reportService.saveSchedule(schedule)
    setReportSchedules((prev) => {
      const exists = prev.some((s) => s.id === schedule.id)
      return exists
        ? prev.map((s) => (s.id === schedule.id ? schedule : s))
        : [...prev, schedule]
    })
  }, [])

  const toggleSchedule = useCallback((id: string) => {
    setReportSchedules((prev) =>
      prev.map((s) => (s.id === id ? { ...s, active: !s.active } : s))
    )
  }, [])

  const deleteSchedule = useCallback(async (id: string) => {
    await reportService.deleteSchedule(id)
    setReportSchedules((prev) => prev.filter((s) => s.id !== id))
  }, [])

  const runDiscovery = useCallback(
    async (mode: discoveryService.DiscoveryMode, input: string) => {
      const candidates = await discoveryService.runDiscovery(mode, input)
      const known = new Set(discoveryCandidates.map((c) => c.slug))
      const fresh = candidates.filter((c) => !known.has(c.slug))
      /* Re-running discovery restores previously dismissed suggestions. */
      const dismissed = discoveryCandidates.filter((c) => c.status === "dismissed").length
      setDiscoveryCandidates((prev) => [
        ...prev.map((c) =>
          c.status === "dismissed" ? { ...c, status: "suggested" as const } : c
        ),
        ...fresh,
      ])
      return fresh.length + dismissed
    },
    [discoveryCandidates]
  )

  const dismissCandidate = useCallback(async (slug: string) => {
    await discoveryService.dismissCandidate(slug)
    setDiscoveryCandidates((prev) =>
      prev.map((c) => (c.slug === slug ? { ...c, status: "dismissed" } : c))
    )
  }, [])

  const markNotRelevant = useCallback(async (slug: string) => {
    await discoveryService.sendFeedback(slug)
    setDiscoveryCandidates((prev) => prev.filter((c) => c.slug !== slug))
  }, [])

  const addConversation = useCallback((title: string) => {
    const id = `c${conversationCounter.current++}`
    setConversations((prev) => [{ id, title, when: "Today" }, ...prev])
    return id
  }, [])

  const renameConversation = useCallback((id: string, title: string) => {
    setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, title } : c)))
  }, [])

  const deleteConversation = useCallback((id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id))
  }, [])

  const updateSettings = useCallback((patch: Partial<WorkspaceSettingsState>) => {
    setSettings((prev) => ({ ...prev, ...patch }))
  }, [])

  const saveSettingsSection = useCallback(
    async <K extends keyof WorkspaceSettingsState>(
      section: K,
      values: WorkspaceSettingsState[K]
    ) => {
      await settingsService.saveSettings(section, values)
      setSettings((prev) => ({ ...prev, [section]: values }))
    },
    []
  )

  const exportWorkspaceSnapshot = useCallback(
    () => ({
      exportedAt: new Date().toISOString(),
      workspace: settings.workspace,
      competitors,
      products,
      changeEvents: changeEvents.map(({ product, ...rest }) => ({
        ...rest,
        product: { slug: product.slug, name: product.name, sku: product.sku },
      })),
      reports,
      reportSchedules,
      watchlist: [...watchlist],
    }),
    [settings.workspace, competitors, products, changeEvents, reports, reportSchedules, watchlist]
  )

  const deleteCompetitorData = useCallback(async (name: string) => {
    await settingsService.deleteCompetitorData(slugify(name))
    setProducts((prev) => prev.filter((p) => p.competitor !== name))
    setChangeEvents((prev) => prev.filter((e) => e.competitor !== name))
  }, [])

  const deleteWorkspace = useCallback(async () => {
    await settingsService.deleteWorkspace()
    setCompetitors([])
    setProducts([])
    setChangeEvents([])
    setReports([])
    setReportSchedules([])
    setDiscoveryCandidates([])
    setWatchlist(new Set())
    setConversations([])
    setSettings(initialSettings())
  }, [])

  const value = useMemo<WorkspaceContextValue>(
    () => ({
      competitors,
      products,
      changeEvents,
      reports,
      reportSchedules,
      discoveryCandidates,
      watchlist,
      conversations,
      settings,
      competitorConfigs,
      getCompetitorConfig: (slug) => competitorConfigs[slug] ?? defaultCompetitorConfig,
      competitorName: (slug) => competitors.find((c) => c.slug === slug)?.name,
      competitorSlug: (name) =>
        competitors.find((c) => c.name === name)?.slug ?? slugify(name),
      runScan,
      addCompetitor,
      monitorCandidate,
      pauseCompetitor,
      resumeCompetitor,
      removeCompetitor,
      saveCompetitorConfig,
      toggleWatchlist,
      addToWatchlist,
      createReport,
      deleteReport,
      saveSchedule,
      toggleSchedule,
      deleteSchedule,
      runDiscovery,
      dismissCandidate,
      markNotRelevant,
      askAI: aiService.askAI,
      addConversation,
      renameConversation,
      deleteConversation,
      updateSettings,
      saveSettingsSection,
      exportWorkspaceSnapshot,
      deleteCompetitorData,
      deleteWorkspace,
    }),
    [
      competitors,
      products,
      changeEvents,
      reports,
      reportSchedules,
      discoveryCandidates,
      watchlist,
      conversations,
      settings,
      competitorConfigs,
      runScan,
      addCompetitor,
      monitorCandidate,
      pauseCompetitor,
      resumeCompetitor,
      removeCompetitor,
      saveCompetitorConfig,
      toggleWatchlist,
      addToWatchlist,
      createReport,
      deleteReport,
      saveSchedule,
      toggleSchedule,
      deleteSchedule,
      runDiscovery,
      dismissCandidate,
      markNotRelevant,
      addConversation,
      renameConversation,
      deleteConversation,
      updateSettings,
      saveSettingsSection,
      exportWorkspaceSnapshot,
      deleteCompetitorData,
      deleteWorkspace,
    ]
  )

  return (
    <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>
  )
}

export function useWorkspace() {
  const ctx = useContext(WorkspaceContext)
  if (!ctx) throw new Error("useWorkspace must be used within WorkspaceProvider")
  return ctx
}
