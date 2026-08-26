import { useEffect, useRef, useState, type ReactNode } from "react"
import { Check } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"

export function SettingsSection({
  title,
  subtitle,
  children,
}: {
  title: string
  subtitle?: string
  children: ReactNode
}) {
  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader>
        <CardTitle className="text-sm font-bold">{title}</CardTitle>
        {subtitle && (
          <CardDescription className="text-xs">{subtitle}</CardDescription>
        )}
      </CardHeader>
      <CardContent className="flex flex-col gap-4">{children}</CardContent>
    </Card>
  )
}

export function FormField({
  label,
  value,
  onChange,
  options,
  error,
  placeholder,
}: {
  label: string
  value: string
  onChange: (value: string) => void
  options?: string[]
  error?: string
  placeholder?: string
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label className="text-xs font-semibold">{label}</Label>
      {options ? (
        <Select value={value} onValueChange={onChange}>
          <SelectTrigger className="h-9 w-full text-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {options.map((o) => (
              <SelectItem key={o} value={o} className="text-xs">
                {o}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      ) : (
        <Input
          value={value}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          className={cn("h-9 text-xs", error && "border-destructive")}
        />
      )}
      {error && <p className="text-[11px] text-destructive">{error}</p>}
    </div>
  )
}

/* Toggle row with optional transient "Saved" confirmation (auto-save). */
export function ToggleRow({
  label,
  description,
  checked,
  onChange,
  autoSave = true,
  disabled = false,
}: {
  label: string
  description?: string
  checked: boolean
  onChange: (checked: boolean) => void
  autoSave?: boolean
  disabled?: boolean
}) {
  const [saved, setSaved] = useState(false)
  const timer = useRef<number | null>(null)
  useEffect(() => () => {
    if (timer.current) window.clearTimeout(timer.current)
  }, [])

  return (
    <div className="flex items-start justify-between gap-4">
      <div className="min-w-0">
        <span className="flex items-center gap-2 text-xs font-semibold">
          {label}
          {saved && (
            <span className="flex items-center gap-0.5 text-[11px] font-medium text-success">
              <Check className="size-3" /> Saved
            </span>
          )}
        </span>
        {description && (
          <p className="mt-0.5 text-[11px] leading-relaxed text-muted-foreground">
            {description}
          </p>
        )}
      </div>
      <Switch
        checked={checked}
        disabled={disabled}
        onCheckedChange={(c) => {
          onChange(c)
          if (autoSave) {
            setSaved(true)
            if (timer.current) window.clearTimeout(timer.current)
            timer.current = window.setTimeout(() => setSaved(false), 1600)
          }
        }}
      />
    </div>
  )
}

export function SaveBar({
  dirty,
  onCancel,
  onSave,
}: {
  dirty: boolean
  onCancel: () => void
  onSave: () => void
}) {
  const [saved, setSaved] = useState(false)
  if (!dirty && !saved) return null
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-primary/20 bg-accent px-3.5 py-2.5">
      {dirty ? (
        <>
          <span className="text-[11px] font-bold text-accent-foreground">
            Unsaved changes
          </span>
          <span className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onCancel}
              className="h-8 rounded-lg bg-card text-[11px] font-semibold"
            >
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={() => {
                onSave()
                setSaved(true)
                window.setTimeout(() => setSaved(false), 1600)
              }}
              className="h-8 rounded-lg text-[11px] font-bold"
            >
              Save changes
            </Button>
          </span>
        </>
      ) : (
        <span className="flex items-center gap-1 text-[11px] font-bold text-success">
          <Check className="size-3.5" /> Saved
        </span>
      )}
    </div>
  )
}

export function UsageBar({
  label,
  display,
  used,
  limit,
}: {
  label: string
  display: string
  used: number
  limit: number
}) {
  return (
    <div>
      <div className="flex items-center justify-between text-[11px]">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium text-foreground">{display}</span>
      </div>
      <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary"
          style={{ width: `${Math.min(100, (used / limit) * 100)}%` }}
        />
      </div>
    </div>
  )
}

export function RadioCards({
  options,
  value,
  onChange,
}: {
  options: { value: string; label: string; hint: string }[]
  value: string
  onChange: (value: string) => void
}) {
  return (
    <div className="grid gap-2 sm:grid-cols-3">
      {options.map((o) => (
        <button
          key={o.value}
          onClick={() => onChange(o.value)}
          className={cn(
            "rounded-xl border p-2.5 text-left transition-colors",
            value === o.value
              ? "border-primary bg-accent"
              : "bg-card hover:border-primary/40"
          )}
        >
          <span className="block text-xs font-bold">{o.label}</span>
          <span className="mt-0.5 block text-[11px] text-muted-foreground">
            {o.hint}
          </span>
        </button>
      ))}
    </div>
  )
}
