/*
 * Mock defaults shaped like the future settings API
 * (GET/PATCH /api/settings/*, /api/team, /api/billing). Settings configure
 * PRODUCT behaviour in business language; Django persists them and the
 * Python services (Celery scheduling, Change Detector, Notification and
 * AI providers) consume them. React is only the configuration interface.
 */

export const workspaceSettings = {
  name: "Acme Toys Ltd",
  website: "https://acmetoys.co.uk",
  market: "United Kingdom",
  industry: "Toys & Games",
  currency: "GBP (£)",
  timezone: "Europe/London",
  dateFormat: "DD/MM/YYYY",
}

export const workspaceOptions = {
  markets: ["United Kingdom", "United States", "Germany", "France", "Romania"],
  industries: ["Toys & Games", "Fashion", "Electronics", "Home & Garden", "Beauty"],
  currencies: ["GBP (£)", "EUR (€)", "USD ($)", "RON (lei)"],
  timezones: ["Europe/London", "Europe/Bucharest", "Europe/Berlin", "America/New_York"],
  dateFormats: ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"],
}

export const monitoringSettings = {
  frequency: "Every 24 hours",
  allowOverrides: true,
  spreadScans: true,
  scope: {
    prices: true,
    stock: true,
    products: true,
    promotions: true,
    names: true,
    categories: true,
  },
  advancedScope: {
    descriptions: false,
    reviewCounts: false,
    badges: false,
    images: false,
  },
  ignoreThreshold: "0",
  confirmRemoved: true,
  status: {
    competitors: "4",
    interval: "24 hours",
    lastActivity: "12 min ago",
  },
}

export const monitoringScopeLabels: Record<string, string> = {
  prices: "Track prices",
  stock: "Track stock",
  products: "Track new/removed products",
  promotions: "Track promotions",
  names: "Track product names",
  categories: "Track categories",
  descriptions: "Track descriptions",
  reviewCounts: "Track review counts",
  badges: "Track badges",
  images: "Track images",
}

export const notificationSettings = {
  inApp: true,
  priorities: { high: true, medium: true, low: false },
  email: true,
  emailAddress: "user@company.com",
  emailOptions: {
    immediateHigh: true,
    dailyDigest: true,
    weeklyReport: true,
    monitoringProblems: true,
  },
  digestTime: "08:00",
  weeklyDay: "Monday",
  weeklyTime: "08:00",
}

export const emailOptionLabels: Record<string, string> = {
  immediateHigh: "Immediate high-priority alerts",
  dailyDigest: "Daily intelligence digest",
  weeklyReport: "Weekly intelligence report",
  monitoringProblems: "Monitoring problems",
}

export const aiSettings = {
  aiAnalysis: true,
  aiInReports: true,
  aiInAlerts: true,
  style: "balanced",
  showEvidence: true,
}

export const aiStyleOptions = [
  { value: "concise", label: "Concise", hint: "Short key insights." },
  { value: "balanced", label: "Balanced", hint: "Recommended default." },
  { value: "detailed", label: "Detailed", hint: "More explanation and context." },
]

export const reportSettings = {
  period: "Last 7 days",
  competitors: "All monitored competitors",
  aiByDefault: true,
  brandingName: "Acme Toys Ltd",
  detail: "standard",
  dailyTime: "08:00",
  weeklyDay: "Monday",
  weeklyTime: "08:00",
}

export const reportDetailOptions = [
  { value: "executive", label: "Executive", hint: "High-level summary only." },
  { value: "standard", label: "Standard", hint: "Recommended default." },
  { value: "detailed", label: "Detailed", hint: "Full data and breakdowns." },
]

export type TeamMember = {
  id: string
  name: string
  email: string
  role: "Owner" | "Admin" | "Analyst" | "Viewer"
  status: "Active" | "Invited"
  lastActive: string
}

export const teamMembers: TeamMember[] = [
  { id: "m1", name: "Daniel Iancu", email: "daniel@acmetoys.co.uk", role: "Owner", status: "Active", lastActive: "Now" },
  { id: "m2", name: "Sarah Jones", email: "sarah@acmetoys.co.uk", role: "Analyst", status: "Active", lastActive: "2h ago" },
  { id: "m3", name: "Alex Popescu", email: "alex@acmetoys.co.uk", role: "Viewer", status: "Active", lastActive: "Yesterday" },
]

export const roleDescriptions = [
  { role: "Owner", description: "Full workspace access." },
  { role: "Admin", description: "Manage competitors, settings and users." },
  { role: "Analyst", description: "View intelligence, create reports/alerts, use Ask AI." },
  { role: "Viewer", description: "Read-only." },
]

export const dataSettings = {
  stats: [
    { label: "Competitors", value: "4" },
    { label: "Products", value: "8,746" },
    { label: "Historical snapshots", value: "Available" },
    { label: "Monitoring since", value: "10 August 2026" },
  ],
  retention: "12 months",
  retentionOptions: ["3 months", "12 months", "24 months"],
  competitors: ["ToyWorld.co.uk", "PlayNest.co.uk", "HappyToyHouse.com", "LittleMindsToys.co.uk"],
}

export const billing = {
  plan: "Growth",
  status: "Active",
  usage: [
    { label: "Competitors", used: 4, limit: 10, display: "4 / 10" },
    { label: "Products monitored", used: 8746, limit: 25000, display: "8,746 / 25,000" },
  ],
  facts: [
    { label: "Scan frequency", value: "Every 12 hours" },
    { label: "Historical data", value: "12 months" },
  ],
}

export const settingsSections = [
  { id: "workspace", label: "Workspace" },
  { id: "monitoring", label: "Monitoring" },
  { id: "notifications", label: "Notifications" },
  { id: "ai", label: "AI" },
  { id: "reports", label: "Reports" },
  { id: "team", label: "Team" },
  { id: "data", label: "Data & Privacy" },
  { id: "billing", label: "Billing" },
] as const

export type SettingsSectionId = (typeof settingsSections)[number]["id"]
