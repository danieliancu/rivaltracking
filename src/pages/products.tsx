import { useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import {
  Download,
  GitCompareArrows,
  Package,
  PackageX,
  Sparkles,
  Tags,
  Trash2,
  type LucideIcon,
} from "lucide-react"
import { toast } from "sonner"

import { productKpis, type ProductRow } from "@/lib/products-data"
import {
  filterProducts,
  productFiltersFromParams,
  productsCsv,
} from "@/lib/product-filters"
import { downloadCsv } from "@/lib/csv"
import { useWorkspace } from "@/lib/workspace-store"
import { Button } from "@/components/ui/button"
import { AIInsightCard } from "@/components/shared/ai-insight-card"
import { KpiCard, type KpiTone } from "@/components/shared/kpi-card"
import { ActiveCategories } from "@/components/products/active-categories"
import { CompareDrawer } from "@/components/products/compare-drawer"
import { PriceMovement } from "@/components/products/price-movement"
import { ProductsTable } from "@/components/products/products-table"

const kpiIcons: Record<string, LucideIcon> = {
  total: Package,
  new: Sparkles,
  price: Tags,
  stock: PackageX,
  removed: Trash2,
}

export function ProductsPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { products, competitorName } = useWorkspace()
  const [selectedSlugs, setSelectedSlugs] = useState<string[]>([])
  const [compareProduct, setCompareProduct] = useState<ProductRow | null>(null)

  const exportFiltered = () => {
    const filters = productFiltersFromParams(searchParams, competitorName)
    const csv = productsCsv(filterProducts(products, filters))
    downloadCsv("competeiq-products.csv", csv.headers, csv.rows)
    toast.success("Export ready", {
      description: `${csv.rows.length} products exported to CSV.`,
    })
  }

  const compareSelected = () => {
    if (selectedSlugs.length < 2) {
      toast.info("Select at least two products to compare.")
      return
    }
    const matched = products.find(
      (p) => selectedSlugs.includes(p.slug) && p.matched
    )
    if (matched) setCompareProduct(matched)
    else
      toast.info("No matched listings", {
        description: "The selected products have no matched competitor listings yet.",
      })
  }

  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <section className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">Products</h1>
          <p className="mt-1 text-xs text-muted-foreground">
            Explore and compare products detected across your monitored
            competitors.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={exportFiltered}
            className="h-9 rounded-lg bg-card text-xs font-bold"
          >
            <Download className="size-4" /> Export
          </Button>
          <Button
            onClick={compareSelected}
            className="h-9 rounded-lg text-xs font-bold shadow-md shadow-primary/25"
          >
            <GitCompareArrows className="size-4" /> Compare products
          </Button>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-3.5 md:grid-cols-3 xl:grid-cols-5">
        {productKpis.map((k) => (
          <KpiCard
            key={k.id}
            icon={kpiIcons[k.id]}
            tone={k.tone as KpiTone}
            value={k.value}
            label={k.label}
          />
        ))}
      </section>

      <AIInsightCard
        title="AI Product Intelligence"
        ctaLabel="Explore with Ask AI"
        onCta={() =>
          navigate("/ask-ai", {
            state: { prompt: "What new products have appeared recently?" },
          })
        }
      >
        <strong className="text-foreground">Outdoor Toys</strong> currently show
        the highest pricing activity.{" "}
        <strong className="text-foreground">ToyWorld.co.uk</strong> reduced
        prices on 31 products in this category, while PlayNest.co.uk added 14
        new products. LEGO and STEM products show the strongest cross-competitor
        overlap.
      </AIInsightCard>

      <section className="grid gap-4 xl:grid-cols-2 xl:items-start">
        <PriceMovement />
        <ActiveCategories />
      </section>

      <ProductsTable urlSync onSelectionChange={setSelectedSlugs} />

      <CompareDrawer
        product={compareProduct}
        onClose={() => setCompareProduct(null)}
      />
    </main>
  )
}
