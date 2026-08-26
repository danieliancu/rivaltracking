import { useLocation, useNavigate } from "react-router-dom"

import { useAlerts } from "@/lib/alerts-store"
import {
  Bell,
  Boxes,
  Compass,
  FileBarChart2,
  GitCompareArrows,
  LayoutDashboard,
  Package,
  Settings,
  Sparkles,
  Zap,
} from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"

const nav = [
  { label: "Overview", icon: LayoutDashboard, route: "/" },
  { label: "Competitors", icon: Boxes, route: "/competitors" },
  { label: "Products", icon: Package, route: "/products" },
  { label: "Changes", icon: GitCompareArrows, route: "/changes" },
  { label: "Reports", icon: FileBarChart2, route: "/reports" },
  { label: "Alerts", icon: Bell, route: "/alerts" },
  { label: "Ask AI", icon: Sparkles, route: "/ask-ai" },
  { label: "Discovery", icon: Compass, route: "/discovery" },
  { label: "Settings", icon: Settings, route: "/settings" },
] as const

const daily = [
  ["New products", "37"],
  ["Price reductions", "64"],
  ["Now out of stock", "31"],
  ["New promotions", "7"],
] as const

export function AppSidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { isMobile, setOpenMobile } = useSidebar()
  const { unreadCount } = useAlerts()

  const isActive = (route?: string) => {
    if (!route) return false
    if (route === "/") return location.pathname === "/"
    return location.pathname.startsWith(route)
  }

  return (
    <Sidebar>
      <SidebarHeader className="h-[72px] justify-center px-4">
        <div className="flex items-center gap-2.5">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-purple text-xl font-extrabold text-primary-foreground shadow-lg shadow-primary/30">
            ◇
          </div>
          <div className="leading-tight">
            <span className="block text-[15px] font-bold">CompeteIQ</span>
            <span className="mt-0.5 block text-[10px] text-muted-foreground">
              Competitor Intelligence
            </span>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-2 py-1">
        <SidebarMenu>
          {nav.map(({ label, icon: Icon, ...item }) => (
            <SidebarMenuItem key={label}>
              <SidebarMenuButton
                isActive={isActive("route" in item ? item.route : undefined)}
                onClick={() => {
                  if ("route" in item && item.route) {
                    navigate(item.route)
                    if (isMobile) setOpenMobile(false)
                  }
                }}
                className="h-9 gap-2.5 rounded-lg text-[13px] font-semibold text-muted-foreground data-[active=true]:text-accent-foreground"
              >
                <Icon className="size-4" />
                <span>{label}</span>
              </SidebarMenuButton>
              {label === "Alerts" && unreadCount > 0 && (
                <SidebarMenuBadge className="min-w-[18px] rounded-full bg-destructive px-1 text-[10px] font-bold text-destructive-foreground">
                  {unreadCount}
                </SidebarMenuBadge>
              )}
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>

      <SidebarFooter className="p-3">
        <div className="rounded-xl border bg-background p-3">
          <div className="mb-2.5 flex items-center gap-1.5 text-xs font-bold">
            <Zap className="size-3.5 text-primary" />
            Daily Intelligence
          </div>
          {daily.map(([label, value]) => (
            <div
              key={label}
              className="flex items-center justify-between py-1 text-[11px] text-muted-foreground"
            >
              <span>{label}</span>
              <span className="font-bold text-foreground">{value}</span>
            </div>
          ))}
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
