"use client"

import { useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { Search } from "lucide-react"

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
import { newsItems } from "@/lib/news"

export function HeaderSearch() {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")

  const filteredItems = useMemo(() => {
    const value = query.trim().toLowerCase()

    if (!value) {
      return newsItems
    }

    return newsItems.filter((item) =>
      [item.title, item.excerpt, item.category, item.author, item.status]
        .join(" ")
        .toLowerCase()
        .includes(value)
    )
  }, [query])

  function goToNewsSearch(value: string) {
    const search = value.trim()
    const params = new URLSearchParams()

    if (search) {
      params.set("q", search)
    }

    setOpen(false)
    router.push(params.size ? `/news?${params.toString()}` : "/news")
  }

  return (
    <>
      <Button
        type="button"
        variant="outline"
        className="w-44 justify-start gap-2 text-muted-foreground sm:w-56"
        onClick={() => setOpen(true)}
      >
        <Search className="size-4" />
        <span className="truncate">Search news</span>
      </Button>
      <CommandDialog
        open={open}
        onOpenChange={setOpen}
        title="Search news"
        description="Search Pulse news stories"
        className="max-w-7xl min-w-3xl"
      >
        <Command
          shouldFilter={false}
          onKeyDown={(event) => {
            if (event.key === "Enter" && query.trim()) {
              event.preventDefault()
              goToNewsSearch(query)
            }
          }}
        >
          <CommandInput
            value={query}
            onValueChange={setQuery}
            placeholder="Search stories, topics, authors..."
          />
          <CommandList>
            <CommandEmpty>No stories found.</CommandEmpty>
            <CommandGroup heading="Stories">
              {filteredItems.map((item) => (
                <CommandItem
                  key={item.id}
                  value={`${item.title} ${item.category} ${item.author}`}
                  onSelect={() => {
                    setOpen(false)
                    router.push(`/news/${item.id}`)
                  }}
                >
                  <div className="min-w-0">
                    <div className="truncate font-medium">{item.title}</div>
                    <div className="truncate text-xs text-muted-foreground">
                      {item.category} / {item.author}
                    </div>
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandGroup heading="Search">
              <CommandItem
                value={`search ${query}`}
                onSelect={() => goToNewsSearch(query)}
              >
                <Search className="size-4" />
                <span className="truncate">
                  Search all news{query.trim() ? ` for "${query.trim()}"` : ""}
                </span>
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </Command>
      </CommandDialog>
    </>
  )
}
