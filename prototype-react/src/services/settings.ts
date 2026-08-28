import { mockOk } from "@/services/mock"

/** Future: PATCH /api/settings/:section */
export function saveSettings<T>(section: string, values: T): Promise<T> {
  void section
  return mockOk(values, 500)
}

/** Future: POST /api/team/invitations */
export function inviteMember(email: string, role: string): Promise<{ email: string; role: string }> {
  return mockOk({ email, role }, 400)
}

/** Future: DELETE /api/data/competitors/:slug (removes historical data —
 *  distinct from stopping monitoring). */
export function deleteCompetitorData(slug: string): Promise<{ slug: string }> {
  return mockOk({ slug }, 700)
}

/** Future: DELETE /api/workspace */
export function deleteWorkspace(): Promise<void> {
  return mockOk(undefined, 700)
}
