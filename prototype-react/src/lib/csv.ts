/*
 * Client-side export helpers. Real exports will eventually come from the
 * backend (e.g. GET /api/products/export) — until then we generate files
 * from the currently loaded mock rows so the buttons do something real.
 */

function downloadBlob(filename: string, blob: Blob) {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement("a")
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

function csvCell(value: string | number | null | undefined): string {
  const text = value == null ? "" : String(value)
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text
}

export function downloadCsv(
  filename: string,
  headers: string[],
  rows: (string | number | null | undefined)[][]
) {
  const lines = [headers, ...rows].map((row) => row.map(csvCell).join(","))
  downloadBlob(filename, new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" }))
}

export function downloadJson(filename: string, data: unknown) {
  downloadBlob(
    filename,
    new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
  )
}
