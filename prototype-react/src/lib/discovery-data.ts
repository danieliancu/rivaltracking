/*
 * Mock data shaped like the future Discovery Engine API (GET /api/discovery,
 * POST /api/discovery/run). Candidates and similarity scores are produced by
 * the Python Discovery Engine — the frontend never fabricates candidates.
 * Only catalogue-profile data exists for unmonitored candidates; price and
 * stock history begin after monitoring starts.
 */

export type DiscoveryCandidateStatus = "suggested" | "monitoring" | "dismissed"

export type CatalogueProfile = {
  products: number
  categories: { name: string; count: number }[]
  priceBand: string
  overlap: string
}

export type DiscoveryCandidate = {
  slug: string
  name: string
  url: string
  match: number
  tone: string
  cluster: string
  status: DiscoveryCandidateStatus
  whyMatch: string[]
  catalogueProfile: CatalogueProfile
}

export const discoveryCandidatesSeed: DiscoveryCandidate[] = [
  {
    slug: "brightkidsplay-com",
    name: "BrightKidsPlay.com",
    url: "brightkidsplay.com",
    match: 82,
    tone: "orange",
    cluster: "Educational Toys",
    status: "suggested",
    whyMatch: [
      "68% catalogue overlap with your monitored competitors",
      "Strong presence in Educational Toys and STEM kits",
      "Similar price band to ToyWorld.co.uk (£10–£90)",
      "Ships to the same UK market",
    ],
    catalogueProfile: {
      products: 1620,
      categories: [
        { name: "Educational Toys", count: 540 },
        { name: "Construction Toys", count: 380 },
        { name: "Outdoor Toys", count: 290 },
      ],
      priceBand: "£8 – £95",
      overlap: "68% catalogue overlap",
    },
  },
  {
    slug: "toycorner-co-uk",
    name: "ToyCorner.co.uk",
    url: "toycorner.co.uk",
    match: 79,
    tone: "blue",
    cluster: "General Toys",
    status: "suggested",
    whyMatch: [
      "61% catalogue overlap across five shared categories",
      "Competes directly on Outdoor Toys pricing",
      "UK-based retailer with comparable catalogue size",
    ],
    catalogueProfile: {
      products: 2210,
      categories: [
        { name: "Outdoor Toys", count: 610 },
        { name: "Plush Toys", count: 420 },
        { name: "Baby Toys", count: 300 },
      ],
      priceBand: "£5 – £120",
      overlap: "61% catalogue overlap",
    },
  },
  {
    slug: "kidsplaystore-co-uk",
    name: "KidsPlayStore.co.uk",
    url: "kidsplaystore.co.uk",
    match: 76,
    tone: "teal",
    cluster: "Outdoor Toys",
    status: "suggested",
    whyMatch: [
      "57% catalogue overlap, concentrated in Outdoor Toys",
      "Frequently discounts the same product lines as ToyWorld",
      "Similar seasonal promotion cadence",
    ],
    catalogueProfile: {
      products: 1480,
      categories: [
        { name: "Outdoor Toys", count: 520 },
        { name: "Garden Play", count: 260 },
        { name: "Sports Toys", count: 190 },
      ],
      priceBand: "£12 – £150",
      overlap: "57% catalogue overlap",
    },
  },
  {
    slug: "smartplaytoys-co-uk",
    name: "SmartPlayToys.co.uk",
    url: "smartplaytoys.co.uk",
    match: 73,
    tone: "purple",
    cluster: "Educational Toys",
    status: "suggested",
    whyMatch: [
      "54% catalogue overlap in Educational and STEM ranges",
      "Overlapping brand portfolio with PlayNest.co.uk",
      "Comparable price positioning",
    ],
    catalogueProfile: {
      products: 980,
      categories: [
        { name: "Educational Toys", count: 460 },
        { name: "Science Kits", count: 210 },
        { name: "Puzzles", count: 140 },
      ],
      priceBand: "£10 – £80",
      overlap: "54% catalogue overlap",
    },
  },
  {
    slug: "gardenplaydirect-com",
    name: "GardenPlayDirect.com",
    url: "gardenplaydirect.com",
    match: 69,
    tone: "orange",
    cluster: "Outdoor Toys",
    status: "suggested",
    whyMatch: [
      "Specialist Outdoor Toys retailer with 48% overlap",
      "Competes on large garden items where your competitors discount",
    ],
    catalogueProfile: {
      products: 720,
      categories: [
        { name: "Outdoor Toys", count: 480 },
        { name: "Garden Play", count: 160 },
      ],
      priceBand: "£25 – £400",
      overlap: "48% catalogue overlap",
    },
  },
  {
    slug: "littleexplorers-co-uk",
    name: "LittleExplorers.co.uk",
    url: "littleexplorers.co.uk",
    match: 66,
    tone: "teal",
    cluster: "General Toys",
    status: "suggested",
    whyMatch: [
      "45% catalogue overlap across Baby and Plush Toys",
      "Growing catalogue in categories your competitors expand into",
    ],
    catalogueProfile: {
      products: 1150,
      categories: [
        { name: "Baby Toys", count: 380 },
        { name: "Plush Toys", count: 310 },
        { name: "Educational Toys", count: 240 },
      ],
      priceBand: "£6 – £70",
      overlap: "45% catalogue overlap",
    },
  },
]

export const discoveryClusters = [
  { id: "Educational Toys", label: "Educational Toys" },
  { id: "Outdoor Toys", label: "Outdoor Toys" },
  { id: "General Toys", label: "General Toys" },
]

export const discoveryModes = [
  { value: "existing", label: "Based on existing competitors" },
  { value: "website", label: "From a website" },
  { value: "category", label: "By category" },
  { value: "brand", label: "By brand" },
  { value: "market", label: "By market" },
] as const

export const discoveryStages = [
  "Analysing your market",
  "Finding candidate companies",
  "Comparing catalogues",
  "Ranking matches",
] as const
