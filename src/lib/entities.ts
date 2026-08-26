import { competitorRows } from "@/lib/competitors-data"

/*
 * Mapping helpers between competitor display names ("ToyWorld.co.uk") and
 * URL-safe slugs ("toyworld-co-uk"). Datasets reference competitors by
 * display name while routes and query params use slugs.
 */

export function slugify(input: string): string {
  return input
    .toLowerCase()
    .replace(/^https?:\/\//, "")
    .replace(/^www\./, "")
    .replace(/\/.*$/, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
}

const nameBySlug = new Map(competitorRows.map((c) => [c.slug, c.name]))
const slugByName = new Map(competitorRows.map((c) => [c.name, c.slug]))

export function slugForCompetitor(name: string): string {
  return slugByName.get(name) ?? slugify(name)
}

export function nameForCompetitor(slug: string): string | undefined {
  if (nameBySlug.has(slug)) return nameBySlug.get(slug)
  /* Fall back to matching store-added competitors by slugified name. */
  return undefined
}

/* Category names ↔ query-param tokens ("Outdoor Toys" ↔ "outdoor-toys"). */
export function categoryParam(name: string): string {
  return slugify(name)
}

export function categoryFromParam(param: string, categories: string[]): string | undefined {
  return categories.find((c) => slugify(c) === param.toLowerCase())
}
