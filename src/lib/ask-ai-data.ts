/*
 * Mock of the future AskAIService. The backend flow is: question → intent
 * detection → controlled Python data services → compact structured context →
 * AIProvider → structured response. React only renders the structured result;
 * facts always come from verified analytics, AI adds interpretation.
 */

export type AIMetric = { label: string; value: string; tone?: string }

export type AIProductResult = {
  name: string
  slug: string
  from: string
  to: string
  pct: string
}

export type AIComparisonRow = {
  competitor: string
  changes: number
  drops: number
  newProducts: number
}

export type AIAction = {
  label: string
  kind: "alert" | "report" | "changes" | "products"
  /* Optional pre-fill for the create-alert dialog. */
  alertPrefill?: { competitor?: string; kind?: string; category?: string }
  /* Optional report type for the create-report dialog. */
  reportTypeId?: string
  /* Optional filtered destination for changes/products navigation. */
  to?: string
}

export type AIResponseData = {
  id: string
  heading: string
  summary?: string
  bullets?: string[]
  metrics?: AIMetric[]
  productList?: { title: string; items: AIProductResult[] }
  comparisonTable?: AIComparisonRow[]
  chart?: { title: string; series: { label: string; value: number }[] }
  interpretation?: string
  nextStep?: string
  recommendations?: string[]
  caveat?: string
  evidence: { label: string; to: string }[]
  followUps: string[]
  actions?: AIAction[]
  dataThrough: string
  lastScan?: string
}

export const suggestedQuestions = [
  { category: "Today", question: "What should I pay attention to today?" },
  { category: "Pricing", question: "Which competitors reduced prices this week?" },
  { category: "Products", question: "What new products have appeared recently?" },
  { category: "Stock", question: "Where are competitors having stock problems?" },
  { category: "Strategy", question: "Is ToyWorld showing signs of a pricing campaign?" },
  { category: "Opportunities", question: "Find potential gaps in competitor catalogues." },
]

export const activitySuggestions = [
  {
    title: "ToyWorld pricing spike",
    detail: "67 changes detected",
    cta: "Ask what changed",
    prompt: "What changed at ToyWorld this week?",
    tone: "bg-success/10 text-success",
  },
  {
    title: "Educational Toys expansion",
    detail: "14 new products detected at PlayNest",
    cta: "Analyse",
    prompt: "What new products have appeared recently?",
    tone: "bg-info/10 text-info",
  },
  {
    title: "Stock activity",
    detail: "18 products unavailable at HappyToyHouse",
    cta: "Investigate",
    prompt: "Where are competitors having stock problems?",
    tone: "bg-warning/10 text-warning",
  },
]

export const conversationHistory = [
  { id: "c1", title: "ToyWorld weekly activity", when: "Today" },
  { id: "c2", title: "Outdoor Toys pricing", when: "Today" },
  { id: "c3", title: "Compare ToyWorld vs PlayNest", when: "Yesterday" },
  { id: "c4", title: "Catalogue opportunities", when: "22 Aug" },
]

const DATA_THROUGH = "25 Aug, 14:42"
const TOYWORLD_SCAN = "Last ToyWorld scan: 12 min ago"

const responses: { match: RegExp; response: AIResponseData }[] = [
  {
    match: /(changed|change|active).*toyworld|toyworld.*(week|changed|activity)/i,
    response: {
      id: "toyworld-week",
      heading: "ToyWorld was highly active this week",
      summary: "428 changes were detected across 2,438 monitored products.",
      bullets: [
        "**186** price decreases",
        "**73** price increases",
        "**31** stock-outs",
        "**37** new products",
        "**7** new promotions",
      ],
      metrics: [
        { label: "Price decreases", value: "186", tone: "text-success" },
        { label: "Price increases", value: "73", tone: "text-destructive" },
        { label: "New products", value: "37" },
        { label: "Stock changes", value: "31" },
      ],
      interpretation:
        "The strongest activity was in Outdoor Toys, where median prices fell by 8.4%. ToyWorld was responsible for approximately 48% of all competitor activity monitored during this period — it appears to be applying concentrated pricing pressure rather than making random isolated adjustments.",
      nextStep:
        "Review your Outdoor Toys pricing and inspect ToyWorld's largest reductions.",
      evidence: [
        { label: "View 186 price changes", to: "/changes" },
        { label: "View 37 new products", to: "/products" },
        { label: "View Outdoor Toys category", to: "/products" },
      ],
      followUps: [
        "Which products had the biggest reductions?",
        "Compare this with PlayNest",
        "Show ToyWorld price activity over the last 30 days",
        "Create an alert for drops over 10%",
      ],
      actions: [
        {
          label: "Create alert",
          kind: "alert",
          alertPrefill: { competitor: "ToyWorld.co.uk", kind: "drop" },
        },
        {
          label: "View in Changes",
          kind: "changes",
          to: "/changes?competitor=toyworld-co-uk",
        },
      ],
      dataThrough: DATA_THROUGH,
      lastScan: TOYWORLD_SCAN,
    },
  },
  {
    match: /attention|investigate today|pay attention|should i (look|investigate)/i,
    response: {
      id: "attention-today",
      heading: "ToyWorld has the highest activity today",
      summary: "ToyWorld accounts for 55% of all detected competitor changes.",
      bullets: [
        "**42** price decreases in Outdoor Toys",
        "Median reduction of **12.4%**",
        "**8** new promotions",
        "**11** products currently out of stock",
      ],
      interpretation:
        "PlayNest is also showing notable activity, primarily through 14 new Educational Toys. The concentration and timing of ToyWorld's reductions suggest a coordinated campaign rather than isolated adjustments.",
      recommendations: [
        "ToyWorld's Outdoor Toys pricing",
        "PlayNest's new Educational Toys",
        "Stock availability at HappyToyHouse",
      ],
      evidence: [
        { label: "View 67 ToyWorld changes", to: "/changes" },
        { label: "View 14 PlayNest products", to: "/products" },
        { label: "View stock activity", to: "/changes" },
      ],
      followUps: [
        "Why do you think ToyWorld is doing this?",
        "Compare ToyWorld with my other competitors",
        "Create a price alert",
      ],
      actions: [{ label: "Create alert", kind: "alert" }],
      dataThrough: DATA_THROUGH,
      lastScan: TOYWORLD_SCAN,
    },
  },
  {
    match: /biggest|largest|drops over|reduced prices|price drops|reductions/i,
    response: {
      id: "biggest-drops",
      heading: "Largest price reductions this week",
      summary:
        "186 price decreases were detected. These are the largest verified reductions:",
      productList: {
        title: "Largest price reductions",
        items: [
          { name: "LEGO Castle Set", slug: "lego-castle-set", from: "£59.99", to: "£49.99", pct: "-16.7%" },
          { name: "STEM Robot Kit", slug: "stem-robot-kit", from: "£47.99", to: "£39.99", pct: "-16.7%" },
          { name: "Wooden Train Set", slug: "wooden-train-set", from: "£37.99", to: "£32.99", pct: "-13.2%" },
        ],
      },
      interpretation:
        "Most of these reductions belong to ToyWorld's Outdoor and Construction Toys ranges, consistent with a concentrated campaign.",
      evidence: [
        { label: "View 42 supporting changes", to: "/changes" },
        { label: "View products", to: "/products" },
      ],
      followUps: [
        "Compare this with PlayNest",
        "Show the last 30 days",
        "Create an alert for drops over 10%",
      ],
      actions: [
        { label: "View in Changes", kind: "changes" },
        { label: "Create alert", kind: "alert" },
      ],
      dataThrough: DATA_THROUGH,
      lastScan: TOYWORLD_SCAN,
    },
  },
  {
    match: /compare/i,
    response: {
      id: "compare",
      heading: "Competitor comparison — this week",
      summary:
        "Verified activity across your four monitored competitors:",
      comparisonTable: [
        { competitor: "ToyWorld.co.uk", changes: 67, drops: 42, newProducts: 11 },
        { competitor: "PlayNest.co.uk", changes: 31, drops: 12, newProducts: 14 },
        { competitor: "HappyToyHouse.com", changes: 19, drops: 8, newProducts: 4 },
        { competitor: "LittleMindsToys.co.uk", changes: 4, drops: 2, newProducts: 1 },
      ],
      interpretation:
        "ToyWorld competes mainly on price while PlayNest competes on catalogue breadth — two different strategies emerging in the same market.",
      caveat:
        "HappyToyHouse has partial monitoring data for today because some product pages could not be checked. Results involving this competitor may be incomplete.",
      evidence: [
        { label: "View competitor activity", to: "/competitors" },
        { label: "View all changes", to: "/changes" },
      ],
      followUps: [
        "Which categories are they discounting?",
        "What is unusual about ToyWorld's behaviour?",
        "Create a Pricing Report",
      ],
      actions: [
        { label: "Create Pricing Report", kind: "report", reportTypeId: "pricing" },
      ],
      dataThrough: DATA_THROUGH,
    },
  },
  {
    match: /price activity|over the last 30|chart|trend/i,
    response: {
      id: "price-chart",
      heading: "ToyWorld price activity — last 30 days",
      summary:
        "Detected price changes per week. Activity accelerated sharply in the most recent week:",
      chart: {
        title: "Price changes per week",
        series: [
          { label: "Week 31", value: 22 },
          { label: "Week 32", value: 31 },
          { label: "Week 33", value: 26 },
          { label: "Week 34", value: 118 },
        ],
      },
      interpretation:
        "The Week 34 spike coincides with the Outdoor Toys reductions — sustained, not a one-day adjustment.",
      evidence: [{ label: "View underlying changes", to: "/changes" }],
      followUps: [
        "Which products had the biggest reductions?",
        "Is this concentrated in one category?",
      ],
      dataThrough: DATA_THROUGH,
      lastScan: TOYWORLD_SCAN,
    },
  },
  {
    match: /new products|appeared|added|launch/i,
    response: {
      id: "new-products",
      heading: "117 new products appeared this month",
      summary:
        "PlayNest leads catalogue expansion, adding 58 products — mostly Educational Toys.",
      metrics: [
        { label: "PlayNest", value: "58" },
        { label: "ToyWorld", value: "21" },
        { label: "HappyToyHouse", value: "22" },
        { label: "LittleMinds", value: "16" },
      ],
      interpretation:
        "Products discovered during initial baseline scans are excluded — these counts reflect only post-baseline additions.",
      evidence: [{ label: "View new products", to: "/products" }],
      followUps: [
        "Which categories are receiving most launches?",
        "Compare launch velocity across competitors",
      ],
      actions: [{ label: "View products", kind: "products" }],
      dataThrough: DATA_THROUGH,
    },
  },
  {
    match: /stock|unavailable|out of stock/i,
    response: {
      id: "stock",
      heading: "Stock problems concentrate at HappyToyHouse",
      summary:
        "91 stock-outs were detected this week. 18 products are currently unavailable at HappyToyHouse, mostly Construction Toys.",
      metrics: [
        { label: "Stock-outs this week", value: "91", tone: "text-warning" },
        { label: "Back in stock", value: "44", tone: "text-success" },
        { label: "Repeated problems", value: "12" },
      ],
      interpretation:
        "Repeated Construction Toys stock-outs may shift demand between competitors — worth watching if your availability is stable.",
      caveat:
        "HappyToyHouse has partial monitoring data for today because some product pages could not be checked. Results involving this competitor may be incomplete.",
      evidence: [{ label: "View stock changes", to: "/changes" }],
      followUps: [
        "Which products are repeatedly out of stock?",
        "Create a stock alert",
      ],
      actions: [{ label: "Create alert", kind: "alert" }],
      dataThrough: DATA_THROUGH,
    },
  },
  {
    match: /gap|opportunit/i,
    response: {
      id: "gaps",
      heading: "Potential catalogue opportunities",
      summary:
        "Based on verified coverage and availability data, two areas stand out as worth investigating:",
      bullets: [
        "**Educational Toys** — expanding rapidly at PlayNest while pricing stays stable elsewhere",
        "**Outdoor Toys availability** — several products frequently unavailable at two competitors",
      ],
      interpretation:
        "These are potential opportunities, not guaranteed gaps — coverage and demand should be verified before acting.",
      evidence: [
        { label: "View category activity", to: "/products" },
        { label: "View stock changes", to: "/changes" },
      ],
      followUps: [
        "Which products are unique to one competitor?",
        "Create a Market Gap report",
      ],
      actions: [
        { label: "Create Pricing Report", kind: "report", reportTypeId: "pricing" },
      ],
      dataThrough: DATA_THROUGH,
    },
  },
]

export const fallbackResponse: AIResponseData = {
  id: "fallback",
  heading: "Today's competitor activity at a glance",
  summary:
    "121 verified changes were detected today across your 4 monitored competitors.",
  metrics: [
    { label: "Changes today", value: "121" },
    { label: "Price decreases", value: "64", tone: "text-success" },
    { label: "New products", value: "37" },
    { label: "Stock changes", value: "31", tone: "text-warning" },
  ],
  interpretation:
    "Most activity concentrates at ToyWorld. Ask me about a competitor, category or product for a deeper analysis.",
  caveat:
    "HappyToyHouse has partial monitoring data for today because some product pages could not be checked. Results involving this competitor may be incomplete.",
  evidence: [{ label: "View today's changes", to: "/changes" }],
  followUps: [
    "What should I pay attention to today?",
    "What changed at ToyWorld this week?",
    "Compare my competitors",
  ],
  dataThrough: DATA_THROUGH,
}

/* Context handed to the AI service alongside the question. The backend
   equivalent is the structured scope object sent to POST /api/ai/query. */
export type AIQueryContext = {
  competitor?: string
  period?: string
  category?: string
  product?: string
  scope?: string
  /* True when the subject is an unmonitored discovery candidate — the AI
     must not pretend historical monitoring data exists. */
  candidate?: boolean
}

function candidateResponse(name: string): AIResponseData {
  return {
    id: `candidate-${name}`,
    heading: `${name} is not monitored yet`,
    summary: `${name} was found by the Discovery Engine, so only its current catalogue profile is available — there is no price or stock history until monitoring starts.`,
    bullets: [
      "**Catalogue profile** — categories and price bands from the discovery comparison",
      "**No change history** — changes are only recorded for monitored competitors",
    ],
    interpretation:
      "Start monitoring this company to build an initial snapshot. Historical comparisons become available after the second successful scan.",
    nextStep: `Monitor ${name} from the Discovery page to start collecting data.`,
    evidence: [{ label: "View discovery results", to: "/discovery" }],
    followUps: [
      "Compare this candidate with my monitored competitors",
      "What should I pay attention to today?",
    ],
    dataThrough: DATA_THROUGH,
  }
}

export function resolveResponse(
  question: string,
  context?: AIQueryContext
): AIResponseData {
  if (context?.candidate && context.competitor) {
    return candidateResponse(context.competitor)
  }
  const base =
    responses.find((r) => r.match.test(question))?.response ?? fallbackResponse
  const scopeParts = [
    context?.competitor,
    context?.product,
    context?.category,
    context?.period,
    context?.scope === "all-competitors" ? "All competitors" : undefined,
  ].filter(Boolean)
  if (scopeParts.length === 0) return base
  return {
    ...base,
    summary: `Scoped to ${scopeParts.join(" · ")}. ${base.summary ?? ""}`.trim(),
  }
}
