import { useMemo, useRef, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { Boxes, Package, Play, Search, Tags } from "lucide-react"
import { toast } from "sonner"

import { ranges, type RangeKey } from "@/lib/data"
import { filterOptions } from "@/lib/products-data"
import { categoryParam } from "@/lib/entities"
import { scanToastMessage } from "@/lib/format"
import { useUiState } from "@/lib/ui-store"
import { useWorkspace } from "@/lib/workspace-store"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Popover, PopoverAnchor, PopoverContent } from "@/components/ui/popover"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function DashboardHeader() {
  const navigate = useNavigate()
  const location = useLocation()
  const { dateRange, setDateRange, selectedCompetitor, scanning } = useUiState()
  const workspace = useWorkspace()

  const [query, setQuery] = useState("")
  const [searchOpen, setSearchOpen] = useState(false)
  const [signOutOpen, setSignOutOpen] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const categories = filterOptions.categories.filter((c) => c !== "All categories")

  const results = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return null
    return {
      competitors: workspace.competitors
        .filter((c) => c.name.toLowerCase().includes(q))
        .slice(0, 4),
      products: workspace.products
        .filter(
          (p) =>
            p.name.toLowerCase().includes(q) || p.sku.toLowerCase().includes(q)
        )
        .slice(0, 5),
      categories: categories.filter((c) => c.toLowerCase().includes(q)).slice(0, 4),
    }
  }, [query, workspace.competitors, workspace.products, categories])

  const closeSearch = () => {
    setSearchOpen(false)
    setQuery("")
  }

  const goTo = (path: string) => {
    closeSearch()
    navigate(path)
  }

  /* Scan context: the competitor detail route wins, then the dashboard
     competitor selector; without either the button opens a picker. */
  const routeSlug = location.pathname.match(/^\/competitors\/([^/?]+)/)?.[1]
  const contextName = routeSlug
    ? workspace.competitorName(routeSlug)
    : selectedCompetitor
      ? workspace.competitorName(selectedCompetitor)
      : undefined

  const startScan = async (name: string) => {
    if (scanning) return
    toast.info("Scan started", { description: `Scanning ${name}…` })
    const result = await workspace.runScan(name)
    const message = scanToastMessage(result)
    toast.success(message.title, { description: message.description })
  }

  const scanButton = (
    <Button
      onClick={contextName ? () => startScan(contextName) : undefined}
      disabled={scanning}
      className="ml-auto h-9 rounded-lg text-xs font-bold shadow-md shadow-primary/25 md:ml-0"
    >
      <Play className="size-3.5 fill-current" />
      {scanning ? "Scanning…" : "Run Scan"}
    </Button>
  )

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b bg-card/90 px-4 backdrop-blur-md md:px-6">
      <SidebarTrigger className="md:hidden" />

      <Popover open={searchOpen && !!results} onOpenChange={(open) => !open && closeSearch()}>
        <PopoverAnchor asChild>
          <div className="relative w-full max-w-md">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              ref={inputRef}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                setSearchOpen(true)
              }}
              onFocus={() => setSearchOpen(true)}
              onKeyDown={(e) => {
                if (e.key === "Escape") closeSearch()
              }}
              placeholder="Search competitors, products or categories..."
              aria-label="Search competitors, products or categories"
              className="h-9 rounded-full bg-card pl-9 text-xs"
            />
          </div>
        </PopoverAnchor>
        <PopoverContent
          align="start"
          className="w-[var(--radix-popover-trigger-width,24rem)] min-w-80 p-0"
          onOpenAutoFocus={(e) => {
            e.preventDefault()
            inputRef.current?.focus()
          }}
        >
          <Command shouldFilter={false}>
            <CommandList>
              {results &&
                results.competitors.length === 0 &&
                results.products.length === 0 &&
                results.categories.length === 0 && (
                  <CommandEmpty>No results for “{query.trim()}”.</CommandEmpty>
                )}
              {results && results.competitors.length > 0 && (
                <CommandGroup heading="Competitors">
                  {results.competitors.map((c) => (
                    <CommandItem
                      key={c.slug}
                      value={`competitor-${c.slug}`}
                      onSelect={() => goTo(`/competitors/${c.slug}`)}
                    >
                      <Boxes /> {c.name}
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
              {results && results.products.length > 0 && (
                <CommandGroup heading="Products">
                  {results.products.map((p) => (
                    <CommandItem
                      key={p.slug}
                      value={`product-${p.slug}`}
                      onSelect={() => goTo(`/products/${p.slug}`)}
                    >
                      <Package /> {p.name}
                      <span className="ml-auto text-[10px] text-muted-foreground">
                        {p.sku}
                      </span>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
              {results && results.categories.length > 0 && (
                <CommandGroup heading="Categories">
                  {results.categories.map((c) => (
                    <CommandItem
                      key={c}
                      value={`category-${c}`}
                      onSelect={() => goTo(`/products?category=${categoryParam(c)}`)}
                    >
                      <Tags /> {c}
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      <Tabs
        value={dateRange}
        onValueChange={(v) => setDateRange(v as RangeKey)}
        className="ml-auto hidden md:block"
      >
        <TabsList className="h-9 rounded-lg">
          {ranges.map((r) => (
            <TabsTrigger
              key={r.key}
              value={r.key}
              className="rounded-md px-3 text-[11px] font-semibold data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
            >
              {r.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {contextName ? (
        scanButton
      ) : (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>{scanButton}</DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel className="text-xs text-muted-foreground">
              Run scan for:
            </DropdownMenuLabel>
            {workspace.competitors.map((c) => (
              <DropdownMenuItem
                key={c.slug}
                onClick={() => startScan(c.name)}
                className="text-xs font-semibold"
              >
                {c.name}
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => startScan("All competitors")}
              className="text-xs font-semibold"
            >
              All competitors
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )}

      <DropdownMenu>
        <DropdownMenuTrigger className="rounded-full outline-none" aria-label="Account menu">
          <Avatar className="size-9">
            <AvatarFallback className="bg-gradient-to-br from-primary to-purple text-[11px] font-extrabold text-primary-foreground">
              DI
            </AvatarFallback>
          </Avatar>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-52">
          <DropdownMenuLabel>
            <span className="block text-sm font-semibold">Dani Iancu</span>
            <span className="block text-[11px] font-normal text-muted-foreground">
              dani@rivaltracking.com
            </span>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => navigate("/settings/team")}>
            Profile
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => navigate("/settings/billing")}>
            Billing
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => navigate("/settings/workspace")}>
            Workspace settings
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => setSignOutOpen(true)}>
            Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <AlertDialog open={signOutOpen} onOpenChange={setSignOutOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Sign out?</AlertDialogTitle>
            <AlertDialogDescription>
              You will be returned to the sign-in screen.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() =>
                toast.info("Authentication is not connected yet", {
                  description: "Sign-in and sign-out arrive with the Django backend.",
                })
              }
            >
              Sign out
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </header>
  )
}
