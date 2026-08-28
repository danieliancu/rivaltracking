import type { ChangeKind } from "@/components/shared/change-badge"
import type { ProductTone } from "@/components/shared/product-identity"

/*
 * Mock data shaped like the future `GET /api/products` response from the
 * Django backend ({ count, results } with server-side search, filtering,
 * sorting and pagination). Presentation components must not hard-code
 * any of these values.
 */

export type MatchedListing = {
  competitor: string
  price: number
  inStock: boolean
  promotion: string | null
  lastScan: string
}

export type ProductRow = {
  slug: string
  name: string
  sku: string
  tone: ProductTone
  competitor: string
  category: string
  currentPrice: number
  /* null while the product only has its initial snapshot (e.g. new products). */
  previousPrice: number | null
  change: { kind: ChangeKind; label: string }
  inStock: boolean
  lastChange: string
  /* Numeric mirror of lastChange for sorting/date-range filtering; the
     backend will return real timestamps instead. */
  lastChangeMinutes: number
  discoveredAt: string
  /* The competitor's live product page. */
  sourceUrl: string
  matched?: {
    count: number
    confidence: number
    insight: string
    listings: MatchedListing[]
  }
}

export const productsResponse = {
  count: 8746,
  results: [
    {
      slug: "lego-castle-set",
      name: "LEGO Castle Set",
      sku: "TW-10432",
      tone: "info",
      competitor: "ToyWorld.co.uk",
      category: "Construction Toys",
      currentPrice: 49.99,
      previousPrice: 59.99,
      change: { kind: "drop", label: "-16.7%" },
      inStock: true,
      lastChange: "2h ago",
      lastChangeMinutes: 120,
      discoveredAt: "2026-03-04",
      sourceUrl: "https://toyworld.co.uk/products/lego-castle-set",
      matched: {
        count: 3,
        confidence: 96,
        insight:
          "ToyWorld is currently £2.49 more expensive than the lowest detected competitor with available stock.",
        listings: [
          { competitor: "ToyWorld.co.uk", price: 49.99, inStock: true, promotion: null, lastScan: "12m ago" },
          { competitor: "PlayNest.co.uk", price: 52.99, inStock: true, promotion: "10% off", lastScan: "26m ago" },
          { competitor: "HappyToyHouse.com", price: 47.5, inStock: false, promotion: null, lastScan: "1h ago" },
        ],
      },
    },
    {
      slug: "stem-robot-kit",
      name: "STEM Robot Kit",
      sku: "TW-20871",
      tone: "purple",
      competitor: "ToyWorld.co.uk",
      category: "Educational Toys",
      currentPrice: 39.99,
      previousPrice: 39.99,
      change: { kind: "promo", label: "20% promotion" },
      inStock: true,
      lastChange: "3h ago",
      lastChangeMinutes: 180,
      discoveredAt: "2026-03-11",
      sourceUrl: "https://toyworld.co.uk/products/stem-robot-kit",
    },
    {
      slug: "wooden-balance-bike",
      name: "Wooden Balance Bike",
      sku: "TW-30114",
      tone: "warning",
      competitor: "ToyWorld.co.uk",
      category: "Outdoor Toys",
      currentPrice: 89,
      previousPrice: 89,
      change: { kind: "oos", label: "Out of stock" },
      inStock: false,
      lastChange: "4h ago",
      lastChangeMinutes: 240,
      discoveredAt: "2026-04-02",
      sourceUrl: "https://toyworld.co.uk/products/wooden-balance-bike",
    },
    {
      slug: "unicorn-plush-xl",
      name: "Unicorn Plush XL",
      sku: "PN-88214",
      tone: "rose",
      competitor: "PlayNest.co.uk",
      category: "Plush Toys",
      currentPrice: 24.99,
      previousPrice: null,
      change: { kind: "new", label: "New product" },
      inStock: true,
      lastChange: "6h ago",
      lastChangeMinutes: 360,
      discoveredAt: "2026-08-25",
      sourceUrl: "https://playnest.co.uk/products/unicorn-plush-xl",
    },
    {
      slug: "personalised-puzzle",
      name: "Personalised Puzzle",
      sku: "HM-50963",
      tone: "teal",
      competitor: "HappyToyHouse.com",
      category: "Personalised Toys",
      currentPrice: 19.99,
      previousPrice: 19.99,
      change: { kind: "name", label: "Name changed" },
      inStock: true,
      lastChange: "8h ago",
      lastChangeMinutes: 480,
      discoveredAt: "2026-04-19",
      sourceUrl: "https://happytoyhouse.com/products/personalised-puzzle",
    },
    {
      slug: "garden-water-table",
      name: "Garden Water Table",
      sku: "PN-11302",
      tone: "info",
      competitor: "PlayNest.co.uk",
      category: "Outdoor Toys",
      currentPrice: 64.99,
      previousPrice: 59.99,
      change: { kind: "increase", label: "+8.3%" },
      inStock: true,
      lastChange: "9h ago",
      lastChangeMinutes: 540,
      discoveredAt: "2026-05-07",
      sourceUrl: "https://playnest.co.uk/products/garden-water-table",
    },
    {
      slug: "baby-sensory-gym",
      name: "Baby Sensory Gym",
      sku: "LM-70415",
      tone: "purple",
      competitor: "LittleMindsToys.co.uk",
      category: "Baby Toys",
      currentPrice: 44.5,
      previousPrice: 44.5,
      change: { kind: "back", label: "Back in stock" },
      inStock: true,
      lastChange: "11h ago",
      lastChangeMinutes: 660,
      discoveredAt: "2026-05-22",
      sourceUrl: "https://littlemindstoys.co.uk/products/baby-sensory-gym",
    },
    {
      slug: "dinosaur-excavation-kit",
      name: "Dinosaur Excavation Kit",
      sku: "HM-61220",
      tone: "warning",
      competitor: "HappyToyHouse.com",
      category: "Educational Toys",
      currentPrice: 14.99,
      previousPrice: 14.99,
      change: { kind: "removed", label: "Removed" },
      inStock: false,
      lastChange: "1d ago",
      lastChangeMinutes: 1440,
      discoveredAt: "2026-03-28",
      sourceUrl: "https://happytoyhouse.com/products/dinosaur-excavation-kit",
    },
    {
      slug: "wooden-train-set",
      name: "Wooden Train Set",
      sku: "LM-33871",
      tone: "teal",
      competitor: "LittleMindsToys.co.uk",
      category: "Construction Toys",
      currentPrice: 32.99,
      previousPrice: 32.99,
      change: { kind: "category", label: "Category changed" },
      inStock: true,
      lastChange: "1d ago",
      lastChangeMinutes: 1500,
      discoveredAt: "2026-06-15",
      sourceUrl: "https://littlemindstoys.co.uk/products/wooden-train-set",
    },
    {
      slug: "stem-coding-kit",
      name: "STEM Coding Kit",
      sku: "LM-90218",
      tone: "purple",
      competitor: "LittleMindsToys.co.uk",
      category: "Educational Toys",
      currentPrice: 54.99,
      previousPrice: 54.99,
      change: { kind: "back", label: "Back in stock" },
      inStock: true,
      lastChange: "10h ago",
      lastChangeMinutes: 600,
      discoveredAt: "2026-04-25",
      sourceUrl: "https://littlemindstoys.co.uk/products/stem-coding-kit",
    },
  ] as ProductRow[],
}

export const productKpis = [
  { id: "total", label: "Total products", value: "8,746", tone: "info" },
  { id: "new", label: "New this week", value: "184", tone: "success" },
  { id: "price", label: "Price changes", value: "312", tone: "purple" },
  { id: "stock", label: "Stock changes", value: "97", tone: "warning" },
  { id: "removed", label: "Removed products", value: "41", tone: "danger" },
] as const

export const priceMovement = {
  decreases: 204,
  increases: 108,
  series: [
    { date: "Apr 23", decreases: 12, increases: 9 },
    { date: "Apr 26", decreases: 16, increases: 11 },
    { date: "Apr 30", decreases: 19, increases: 12 },
    { date: "May 3", decreases: 22, increases: 10 },
    { date: "May 7", decreases: 24, increases: 13 },
    { date: "May 10", decreases: 27, increases: 12 },
    { date: "May 14", decreases: 25, increases: 14 },
    { date: "May 17", decreases: 28, increases: 13 },
    { date: "May 21", decreases: 31, increases: 14 },
  ],
}

export const activeCategories = [
  { name: "Outdoor Toys", changes: 82 },
  { name: "Educational Toys", changes: 67 },
  { name: "Construction Toys", changes: 51 },
  { name: "Plush Toys", changes: 34 },
  { name: "Baby Toys", changes: 28 },
]

export const filterOptions = {
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
  changeTypes: [
    { value: "all", label: "All changes" },
    { value: "new", label: "New product" },
    { value: "drop", label: "Price decrease" },
    { value: "increase", label: "Price increase" },
    { value: "oos", label: "Out of stock" },
    { value: "back", label: "Back in stock" },
    { value: "removed", label: "Removed" },
    { value: "name", label: "Name changed" },
    { value: "category", label: "Category changed" },
    { value: "promo", label: "Promotion detected" },
  ],
  stock: [
    { value: "all", label: "All" },
    { value: "in", label: "In stock" },
    { value: "out", label: "Out of stock" },
  ],
  dateRanges: ["Today", "7 days", "30 days", "Custom"],
}

export const sortOptions = [
  { value: "recent", label: "Most recent change" },
  { value: "price-low", label: "Lowest price" },
  { value: "price-high", label: "Highest price" },
  { value: "biggest-drop", label: "Biggest price decrease" },
  { value: "biggest-increase", label: "Biggest price increase" },
  { value: "newest", label: "Newest discovered" },
  { value: "name", label: "Product name" },
] as const

export type SortValue = (typeof sortOptions)[number]["value"]
