import { useNavigate } from "react-router-dom"

import { AIInsightCard } from "@/components/shared/ai-insight-card"

export function AiSummary() {
  const navigate = useNavigate()
  return (
    <AIInsightCard
      title="AI Summary"
      ctaLabel="View analysis"
      onCta={() =>
        navigate("/ask-ai", {
          state: {
            context: { competitor: "ToyWorld.co.uk", category: "Outdoor Toys" },
            prompt: "What changed at ToyWorld this week?",
          },
        })
      }
    >
      ToyWorld appears to be running a promotion across{" "}
      <strong className="text-foreground">Outdoor Toys</strong>. 62% of recent
      discounts are in this category. Median prices in Outdoor Toys fell by{" "}
      <strong className="text-foreground">8.4% over the last 48 hours</strong>.
      Suggested action: review your Outdoor Toys pricing and monitor LEGO and
      STEM kits.
    </AIInsightCard>
  )
}
