import { mockOk } from "@/services/mock"

/** Future: POST /api/watchlist (conceptually an AlertRule subscription —
 *  watchlist notifications are delivered through the Alert Engine). */
export function addToWatchlist(slugs: string[]): Promise<{ added: number }> {
  return mockOk({ added: slugs.length }, 300)
}

/** Future: DELETE /api/watchlist/:slug */
export function removeFromWatchlist(slug: string): Promise<{ slug: string }> {
  return mockOk({ slug }, 300)
}
