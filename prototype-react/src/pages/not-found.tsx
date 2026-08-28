import { useNavigate } from "react-router-dom"
import { Compass } from "lucide-react"

import { Card } from "@/components/ui/card"
import { EmptyState } from "@/components/shared/empty-state"

export function NotFoundPage() {
  const navigate = useNavigate()
  return (
    <main className="flex flex-col gap-5 p-4 pb-8 md:p-6 lg:px-7">
      <Card className="rounded-xl shadow-sm">
        <EmptyState
          icon={Compass}
          heading="Page not found"
          text="The page you are looking for does not exist or has moved."
          actionLabel="Back to overview"
          onAction={() => navigate("/")}
        />
      </Card>
    </main>
  )
}
