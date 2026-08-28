import { ArrowUp } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function AIComposer({
  value,
  placeholder = "Ask about your competitors...",
  large = false,
  onChange,
  onSend,
}: {
  value: string
  placeholder?: string
  large?: boolean
  onChange: (value: string) => void
  onSend: () => void
}) {
  return (
    <div className="relative w-full">
      <Input
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && value.trim()) onSend()
        }}
        className={large ? "h-12 rounded-xl pr-12 text-sm" : "h-10 rounded-xl pr-12 text-xs"}
      />
      <Button
        size="icon"
        disabled={!value.trim()}
        onClick={onSend}
        className={
          large
            ? "absolute right-1.5 top-1.5 size-9 rounded-lg"
            : "absolute right-1 top-1 size-8 rounded-lg"
        }
      >
        <ArrowUp className="size-4" />
      </Button>
    </div>
  )
}
