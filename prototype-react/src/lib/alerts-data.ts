import type { LucideIcon } from "lucide-react"
import {
  Activity,
  BadgePercent,
  Package,
  PackageX,
  Tags,
} from "lucide-react"

import type { ChangeKind } from "@/components/shared/change-badge"
import type { ImpactLevel } from "@/components/shared/impact-badge"

/*
 * Mock data shaped like the future Alert Engine API
 * (GET/POST /api/alerts/rules, GET /api/alerts, POST /api/alerts/:id/read).
 * Alert conditions are evaluated deterministically by the Python backend
 * against ChangeEvents/ChangePatterns; AI only interprets triggered alerts.
 * Technical keys (event_type, operator, threshold) stay in data — never in UI.
 */

export type AlertTypeGroup = "price" | "stock" | "products" | "promotions" | "patterns"

export const typeGroupMeta: Record<
  AlertTypeGroup,
  { label: string; icon: LucideIcon; tone: string }
> = {
  price: { label: "Price", icon: Tags, tone: "bg-success/10 text-success" },
  stock: { label: "Stock", icon: PackageX, tone: "bg-warning/10 text-warning" },
  products: { label: "Products", icon: Package, tone: "bg-info/10 text-info" },
  promotions: { label: "Promotions", icon: BadgePercent, tone: "bg-purple/10 text-purple" },
  patterns: { label: "Patterns", icon: Activity, tone: "bg-teal/10 text-teal" },
}

export type AlertRule = {
  id: string
  name: string
  typeGroup: AlertTypeGroup
  condition: string
  competitors: string
  category?: string
  frequency: string
  lastTriggered: string
  /* Numeric mirror of lastTriggered for sorting; the backend will return
     real timestamps instead. */
  lastTriggeredMinutes?: number
  active: boolean
  priority?: ImpactLevel
  patternBased?: boolean
  createdAt: string
}

export const alertRules: AlertRule[] = [
  {
    id: "toyworld-drops",
    name: "Large ToyWorld price drops",
    typeGroup: "price",
    condition: "Price decreases by more than 10%",
    competitors: "ToyWorld.co.uk",
    frequency: "Immediate",
    lastTriggered: "12 min ago",
    lastTriggeredMinutes: 12,
    active: true,
    priority: "high",
    createdAt: "2026-06-02",
  },
  {
    id: "outdoor-stockouts",
    name: "Outdoor Toys stock-outs",
    typeGroup: "stock",
    condition: "Product goes out of stock",
    competitors: "All competitors",
    category: "Outdoor Toys",
    frequency: "Immediate",
    lastTriggered: "2h ago",
    lastTriggeredMinutes: 120,
    active: true,
    priority: "medium",
    createdAt: "2026-06-18",
  },
  {
    id: "new-educational",
    name: "New Educational Toys",
    typeGroup: "products",
    condition: "New product detected",
    competitors: "All competitors",
    category: "Educational Toys",
    frequency: "Daily summary",
    lastTriggered: "Today, 08:00",
    lastTriggeredMinutes: 400,
    active: true,
    createdAt: "2026-07-01",
  },
  {
    id: "toyworld-promos",
    name: "ToyWorld promotions",
    typeGroup: "promotions",
    condition: "Promotion starts",
    competitors: "ToyWorld.co.uk",
    frequency: "Immediate",
    lastTriggered: "Yesterday",
    lastTriggeredMinutes: 1440,
    active: true,
    createdAt: "2026-07-14",
  },
  {
    id: "major-campaign",
    name: "Major competitor campaign",
    typeGroup: "patterns",
    condition: "20+ related price changes within 6 hours",
    competitors: "All competitors",
    frequency: "Immediate",
    lastTriggered: "3h ago",
    lastTriggeredMinutes: 180,
    active: true,
    priority: "high",
    patternBased: true,
    createdAt: "2026-07-22",
  },
  {
    id: "playnest-increases",
    name: "PlayNest price increases",
    typeGroup: "price",
    condition: "Price increases by more than 5%",
    competitors: "PlayNest.co.uk",
    frequency: "Hourly summary",
    lastTriggered: "3 days ago",
    lastTriggeredMinutes: 4320,
    active: false,
    createdAt: "2026-08-02",
  },
]

export type RecentAlert = {
  id: number
  ruleId: string
  ruleName: string
  event: string
  kind: ChangeKind
  competitor: string
  product?: string
  productSlug?: string
  patternLabel?: string
  isPattern?: boolean
  category?: string
  priority: ImpactLevel
  triggered: string
  detectedAt: string
  status: "new" | "viewed"
  /* Factual "Why you received this alert" content. */
  rule: { scope: string; condition: string; detected: string }
  evidence?: {
    previous: string
    current: string
    difference: string
    change: string
    stock: string
    category: string
  }
  aiNote: string
}

export const initialRecentAlerts: RecentAlert[] = [
  {
    id: 5531,
    ruleId: "toyworld-drops",
    ruleName: "Large ToyWorld price drops",
    event: "Price decreased 16.7%",
    kind: "drop",
    competitor: "ToyWorld.co.uk",
    product: "LEGO Castle Set",
    productSlug: "lego-castle-set",
    priority: "high",
    triggered: "12 min ago",
    detectedAt: "25 Aug, 14:32",
    status: "new",
    rule: {
      scope: "ToyWorld.co.uk",
      condition: "Price decrease > 10%",
      detected: "-16.67%",
    },
    evidence: {
      previous: "£59.99",
      current: "£49.99",
      difference: "-£10.00",
      change: "-16.67%",
      stock: "In stock",
      category: "Construction Toys",
    },
    aiNote:
      "This price reduction is part of a broader pricing movement. ToyWorld has reduced 42 products across Outdoor Toys and Construction Toys during the last six hours.",
  },
  {
    id: 5530,
    ruleId: "major-campaign",
    ruleName: "Major competitor campaign",
    event: "42 related price reductions",
    kind: "drop",
    competitor: "ToyWorld.co.uk",
    patternLabel: "42 related price reductions",
    isPattern: true,
    category: "Outdoor Toys",
    priority: "high",
    triggered: "3h ago",
    detectedAt: "25 Aug, 11:05",
    status: "new",
    rule: {
      scope: "All competitors",
      condition: "20+ related price changes within 6 hours",
      detected: "42 related changes in 5h 40m",
    },
    aiNote:
      "The scale and timing of these reductions suggest a coordinated Outdoor Toys campaign rather than isolated adjustments.",
  },
  {
    id: 5529,
    ruleId: "new-educational",
    ruleName: "New Educational Toys",
    event: "5 new products detected",
    kind: "new",
    competitor: "PlayNest.co.uk",
    patternLabel: "5 new products detected",
    isPattern: true,
    category: "Educational Toys",
    priority: "medium",
    triggered: "Today, 08:00",
    detectedAt: "25 Aug, 08:00",
    status: "new",
    rule: {
      scope: "All competitors · Educational Toys",
      condition: "New product detected (daily summary)",
      detected: "5 new products since yesterday",
    },
    aiNote:
      "PlayNest continues to expand Educational Toys — 24 products added this week, concentrated in STEM and coding kits.",
  },
  {
    id: 5528,
    ruleId: "outdoor-stockouts",
    ruleName: "Outdoor Toys stock-outs",
    event: "Out of stock",
    kind: "oos",
    competitor: "ToyWorld.co.uk",
    product: "Wooden Balance Bike",
    productSlug: "wooden-balance-bike",
    priority: "medium",
    triggered: "2h ago",
    detectedAt: "25 Aug, 12:14",
    status: "viewed",
    rule: {
      scope: "All competitors · Outdoor Toys",
      condition: "Product goes out of stock",
      detected: "Stock changed: In stock → Out of stock",
    },
    evidence: {
      previous: "In stock",
      current: "Out of stock",
      difference: "—",
      change: "Stock status",
      stock: "Out of stock",
      category: "Outdoor Toys",
    },
    aiNote:
      "Outdoor Toys stock-outs at ToyWorld coincide with their discount campaign — demand may be depleting discounted lines.",
  },
  {
    id: 5527,
    ruleId: "outdoor-stockouts",
    ruleName: "Outdoor Toys stock-outs",
    event: "Back in stock",
    kind: "back",
    competitor: "LittleMindsToys.co.uk",
    product: "STEM Coding Kit",
    productSlug: "stem-coding-kit",
    priority: "low",
    triggered: "10h ago",
    detectedAt: "25 Aug, 03:18",
    status: "new",
    rule: {
      scope: "All competitors · Outdoor Toys",
      condition: "Stock status changes",
      detected: "Stock changed: Out of stock → In stock",
    },
    evidence: {
      previous: "Out of stock",
      current: "In stock",
      difference: "—",
      change: "Stock status",
      stock: "In stock",
      category: "Educational Toys",
    },
    aiNote:
      "This product returned after 9 days out of stock. Restocks in Educational Toys often precede promotional pushes.",
  },
  {
    id: 5526,
    ruleId: "toyworld-promos",
    ruleName: "ToyWorld promotions",
    event: "Promotion started: 20% off",
    kind: "promo",
    competitor: "ToyWorld.co.uk",
    product: "STEM Robot Kit",
    productSlug: "stem-robot-kit",
    priority: "medium",
    triggered: "Yesterday",
    detectedAt: "24 Aug, 10:36",
    status: "new",
    rule: {
      scope: "ToyWorld.co.uk",
      condition: "Promotion starts",
      detected: "New promotion: 20% off",
    },
    evidence: {
      previous: "No promotion",
      current: "20% off",
      difference: "—",
      change: "Promotion",
      stock: "In stock",
      category: "Educational Toys",
    },
    aiNote:
      "ToyWorld started 5 promotions in Educational Toys this week — likely part of a wider seasonal campaign.",
  },
]

export const alertKpis = [
  { id: "active", label: "Active alerts", value: "8", tone: "info" },
  { id: "triggered", label: "Triggered today", value: "14", tone: "purple" },
  { id: "high", label: "High priority", value: "3", tone: "warning" },
  { id: "covered", label: "Competitors covered", value: "4", tone: "teal" },
] as const

export const alertActivity = {
  Today: [
    { label: "00:00", price: 0, stock: 0, product: 0, promotions: 0 },
    { label: "04:00", price: 1, stock: 1, product: 0, promotions: 0 },
    { label: "08:00", price: 2, stock: 0, product: 1, promotions: 0 },
    { label: "12:00", price: 5, stock: 1, product: 1, promotions: 1 },
    { label: "16:00", price: 1, stock: 0, product: 0, promotions: 0 },
    { label: "20:00", price: 0, stock: 0, product: 0, promotions: 0 },
  ],
  "7D": [
    { label: "19 Aug", price: 3, stock: 2, product: 1, promotions: 0 },
    { label: "20 Aug", price: 4, stock: 1, product: 2, promotions: 1 },
    { label: "21 Aug", price: 2, stock: 3, product: 1, promotions: 0 },
    { label: "22 Aug", price: 9, stock: 2, product: 2, promotions: 1 },
    { label: "23 Aug", price: 7, stock: 1, product: 3, promotions: 0 },
    { label: "24 Aug", price: 5, stock: 2, product: 1, promotions: 2 },
    { label: "25 Aug", price: 9, stock: 2, product: 2, promotions: 1 },
  ],
  "30D": [
    { label: "Week 31", price: 14, stock: 8, product: 6, promotions: 3 },
    { label: "Week 32", price: 18, stock: 11, product: 9, promotions: 4 },
    { label: "Week 33", price: 12, stock: 7, product: 11, promotions: 2 },
    { label: "Week 34", price: 39, stock: 12, product: 12, promotions: 5 },
  ],
}

export const mostTriggeredRules = [
  { name: "Large ToyWorld price drops", count: 18 },
  { name: "Outdoor stock-outs", count: 11 },
  { name: "New Educational Toys", count: 7 },
  { name: "Promotion started", count: 5 },
]

export const alertCoverage = [
  { label: "Active rules", value: "8" },
  { label: "Competitors covered", value: "4" },
  { label: "Categories monitored", value: "6" },
  { label: "High-priority rules", value: "3" },
]

/* Step 1 trigger catalog — business language only, no event-type codes. */
export const alertTriggerGroups: {
  group: string
  typeGroup: AlertTypeGroup
  options: { id: string; label: string }[]
}[] = [
  {
    group: "Price",
    typeGroup: "price",
    options: [
      { id: "price-decrease", label: "Price decreases" },
      { id: "price-increase", label: "Price increases" },
      { id: "price-change", label: "Price changes" },
    ],
  },
  {
    group: "Stock",
    typeGroup: "stock",
    options: [
      { id: "stock-out", label: "Goes out of stock" },
      { id: "stock-back", label: "Comes back in stock" },
    ],
  },
  {
    group: "Products",
    typeGroup: "products",
    options: [
      { id: "product-new", label: "New product" },
      { id: "product-removed", label: "Product removed" },
    ],
  },
  {
    group: "Promotions",
    typeGroup: "promotions",
    options: [
      { id: "promo-start", label: "Promotion starts" },
      { id: "promo-change", label: "Promotion changes" },
      { id: "promo-end", label: "Promotion ends" },
    ],
  },
  {
    group: "Competitor activity",
    typeGroup: "patterns",
    options: [
      { id: "unusual-activity", label: "Unusual activity" },
      { id: "related-changes", label: "Large group of related changes" },
    ],
  },
]

export const alertFormOptions = {
  competitors: [
    "All competitors",
    "ToyWorld.co.uk",
    "PlayNest.co.uk",
    "HappyToyHouse.com",
    "LittleMindsToys.co.uk",
  ],
  categories: [
    "All categories",
    "Outdoor Toys",
    "Educational Toys",
    "Construction Toys",
    "Baby Toys",
    "Plush Toys",
    "Personalised Toys",
  ],
  operators: ["more than", "less than"],
  priorities: [
    { value: "high", label: "High", hint: "Important business activity." },
    { value: "medium", label: "Medium", hint: "Worth monitoring." },
    { value: "low", label: "Low", hint: "Informational." },
  ],
  frequencies: [
    { value: "Immediate", hint: "Send whenever a matching new event occurs." },
    { value: "Hourly summary", hint: "Group matching alerts within an hour." },
    { value: "Daily summary", hint: "Send one digest per day." },
    { value: "Weekly summary", hint: "For low-priority monitoring." },
  ],
}

export const alertFilterOptions = {
  statuses: [
    { value: "all", label: "All statuses" },
    { value: "active", label: "Active" },
    { value: "paused", label: "Paused" },
  ],
  types: [
    { value: "all", label: "All types" },
    { value: "price", label: "Price" },
    { value: "stock", label: "Stock" },
    { value: "products", label: "Products" },
    { value: "promotions", label: "Promotions" },
    { value: "patterns", label: "Patterns" },
  ],
  sorts: [
    { value: "triggered", label: "Recently triggered" },
    { value: "created", label: "Recently created" },
    { value: "priority", label: "Priority" },
    { value: "name", label: "Name" },
  ],
}
