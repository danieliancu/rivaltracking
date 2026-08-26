import { createContext, useContext, useMemo, useState, type ReactNode } from "react"

import type { RangeKey } from "@/lib/data"

/* High-churn UI state shared across the shell: the global date range,
   the dashboard competitor context and the shared scanning flag (one scan
   at a time — the real work happens in Django/Celery). */

type UiStateContextValue = {
  dateRange: RangeKey
  setDateRange: (range: RangeKey) => void
  selectedCompetitor: string | null
  setSelectedCompetitor: (slug: string | null) => void
  scanning: boolean
  setScanning: (scanning: boolean) => void
}

const UiStateContext = createContext<UiStateContextValue | null>(null)

export function UiStateProvider({ children }: { children: ReactNode }) {
  const [dateRange, setDateRange] = useState<RangeKey>("30d")
  const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(null)
  const [scanning, setScanning] = useState(false)

  const value = useMemo<UiStateContextValue>(
    () => ({
      dateRange,
      setDateRange,
      selectedCompetitor,
      setSelectedCompetitor,
      scanning,
      setScanning,
    }),
    [dateRange, selectedCompetitor, scanning]
  )

  return <UiStateContext.Provider value={value}>{children}</UiStateContext.Provider>
}

export function useUiState() {
  const ctx = useContext(UiStateContext)
  if (!ctx) throw new Error("useUiState must be used within UiStateProvider")
  return ctx
}
