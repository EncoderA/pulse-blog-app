"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { Loader2, Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import type { PostSummary } from "@/lib/api"

function formatDate(dateStr: string | null): string {
  if (!dateStr) return ""
  try {
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    })
  } catch {
    return dateStr
  }
}

export function HeaderSearch() {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<PostSummary[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // ── Keyboard shortcut: ⌘K / Ctrl+K ────────────────────────────────────────
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        setOpen((v) => !v)
      }
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [])

  // ── Reset state when dialog closes ─────────────────────────────────────────
  useEffect(() => {
    if (!open) {
      setQuery("")
      setResults([])
      setError(null)
    }
  }, [open])

  // ── Debounced live search via FastAPI ──────────────────────────────────────
  const runSearch = useCallback(async (q: string) => {
    const trimmed = q.trim()
    if (!trimmed) {
      setResults([])
      setError(null)
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      // Call the Next.js proxy route — same origin, no CORS
      const res = await fetch(`/api/search?q=${encodeURIComponent(trimmed)}`, {
        cache: "no-store",
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setResults(data.posts ?? [])
    } catch {
      setError("Search failed. Is the API running?")
      setResults([])
    } finally {
      setIsLoading(false)
    }
  }, [])

  function onQueryChange(value: string) {
    setQuery(value)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => runSearch(value), 300)
  }

  // ── Navigate to full search results page ───────────────────────────────────
  function goToSearchPage(q: string) {
    const trimmed = q.trim()
    setOpen(false)
    if (trimmed) {
      router.push(`/news?q=${encodeURIComponent(trimmed)}`)
    } else {
      router.push("/news")
    }
  }

  return (
    <>
      <Button
        id="header-search-button"
        type="button"
        variant="outline"
        className="w-44 justify-start gap-2 text-muted-foreground sm:w-56"
        onClick={() => setOpen(true)}
      >
        <Search className="size-4" />
        <span className="truncate">Search news</span>
        <kbd className="ml-auto hidden rounded border bg-muted px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground sm:block">
          ⌘K
        </kbd>
      </Button>

      <CommandDialog
        open={open}
        onOpenChange={setOpen}
        title="Search news"
        description="Search Pulse news stories via the API"
        className="max-w-7xl min-w-3xl"
      >
        <Command
          shouldFilter={false}
          onKeyDown={(e) => {
            if (e.key === "Enter" && query.trim()) {
              e.preventDefault()
              goToSearchPage(query)
            }
          }}
        >
          <div className="relative">
            <CommandInput
              id="header-search-input"
              value={query}
              onValueChange={onQueryChange}
              placeholder="Search stories, topics, keywords..."
            />
            {isLoading && (
              <Loader2 className="absolute right-3 top-1/2 size-4 -translate-y-1/2 animate-spin text-muted-foreground" />
            )}
          </div>

          <CommandList>
            {/* Error state */}
            {error && (
              <div className="px-4 py-3 text-sm text-destructive">{error}</div>
            )}

            {/* Empty state — only show after a query with no results and no error */}
            {!isLoading && !error && query.trim() && results.length === 0 && (
              <CommandEmpty>No stories found for &quot;{query.trim()}&quot;.</CommandEmpty>
            )}

            {/* Live results */}
            {results.length > 0 && (
              <CommandGroup heading={`Stories (${results.length})`}>
                {results.map((post) => (
                  <CommandItem
                    key={post.Id}
                    value={`${post.Id} ${post.Title}`}
                    onSelect={() => {
                      setOpen(false)
                      router.push(`/news/${post.Id}`)
                    }}
                    className="gap-3"
                  >
                    <div className="min-w-0 flex-1">
                      <div className="truncate font-medium">
                        {post.Title ?? "Untitled"}
                      </div>
                      <div className="flex items-center gap-2 truncate text-xs text-muted-foreground">
                        {post.Focus_Area && (
                          <span className="rounded-full bg-muted px-1.5 py-0.5">
                            {post.Focus_Area}
                          </span>
                        )}
                        {post.Date && <span>{formatDate(post.Date)}</span>}
                      </div>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}

            {/* "View all results" action */}
            <CommandGroup heading="Search">
              <CommandItem
                id="header-search-view-all"
                value={`search-all ${query}`}
                onSelect={() => goToSearchPage(query)}
              >
                <Search className="size-4 shrink-0" />
                <span className="truncate">
                  {query.trim()
                    ? `View all results for "${query.trim()}"`
                    : "Browse all stories"}
                </span>
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </Command>
      </CommandDialog>
    </>
  )
}
