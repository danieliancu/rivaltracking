import { mockOk } from "@/services/mock"
import { discoveryCandidatesSeed, type DiscoveryCandidate } from "@/lib/discovery-data"

export type DiscoveryMode = "existing" | "website" | "category" | "brand" | "market"

/** Future: POST /api/discovery/run (Discovery Engine — candidates and
 *  similarity are produced by the Python backend, never invented here). */
export function runDiscovery(
  mode: DiscoveryMode,
  input: string
): Promise<DiscoveryCandidate[]> {
  void mode
  void input
  return mockOk(discoveryCandidatesSeed, 400)
}

/** Future: POST /api/discovery/:id/dismiss */
export function dismissCandidate(slug: string): Promise<{ slug: string }> {
  return mockOk({ slug }, 300)
}

/** Future: POST /api/discovery/:id/feedback ("not relevant" signal that
 *  tunes future candidate ranking). */
export function sendFeedback(slug: string): Promise<{ slug: string }> {
  return mockOk({ slug }, 300)
}
