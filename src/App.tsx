import { BrowserRouter, Route, Routes } from "react-router-dom"

import { AlertsProvider } from "@/lib/alerts-store"
import { UiStateProvider } from "@/lib/ui-store"
import { WorkspaceProvider } from "@/lib/workspace-store"
import { AppSidebar } from "@/components/dashboard/app-sidebar"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { Toaster } from "@/components/ui/sonner"
import { AlertsPage } from "@/pages/alerts"
import { AskAIPage } from "@/pages/ask-ai"
import { ChangesPage } from "@/pages/changes"
import { CompetitorDetailsPage } from "@/pages/competitor-details"
import { CompetitorsPage } from "@/pages/competitors"
import { DiscoveryPage } from "@/pages/discovery"
import { NotFoundPage } from "@/pages/not-found"
import { OverviewPage } from "@/pages/overview"
import { ProductDetailsPage } from "@/pages/product-details"
import { ProductsPage } from "@/pages/products"
import { ReportDetailsPage } from "@/pages/report-details"
import { ReportsPage } from "@/pages/reports"
import { SettingsPage } from "@/pages/settings"

function App() {
  return (
    <BrowserRouter>
      <UiStateProvider>
        <WorkspaceProvider>
          <AlertsProvider>
            <SidebarProvider>
              <AppSidebar />
              <SidebarInset>
                <DashboardHeader />
                <Routes>
                  <Route path="/" element={<OverviewPage />} />
                  <Route path="/competitors" element={<CompetitorsPage />} />
                  <Route path="/competitors/:slug" element={<CompetitorDetailsPage />} />
                  <Route path="/products" element={<ProductsPage />} />
                  <Route path="/products/:slug" element={<ProductDetailsPage />} />
                  <Route path="/changes" element={<ChangesPage />} />
                  <Route path="/reports" element={<ReportsPage />} />
                  <Route path="/reports/:id" element={<ReportDetailsPage />} />
                  <Route path="/alerts" element={<AlertsPage />} />
                  <Route path="/ask-ai" element={<AskAIPage />} />
                  <Route path="/discovery" element={<DiscoveryPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="/settings/:section" element={<SettingsPage />} />
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </SidebarInset>
            </SidebarProvider>
            <Toaster position="bottom-right" />
          </AlertsProvider>
        </WorkspaceProvider>
      </UiStateProvider>
    </BrowserRouter>
  )
}

export default App
