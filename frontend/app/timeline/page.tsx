import Link from "next/link"
import { ArrowUpRight, Newspaper } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { getTimelinePosts } from "@/lib/api"

export default async function TimelinePage() {
  const timelineStories = await getTimelinePosts()

  return (
    <main className="mx-auto flex w-full flex-1 flex-col gap-4 px-4 py-6 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-3">
        <div className="max-w-3xl">
          <Badge variant="secondary" className="mb-2">
            Timeline
          </Badge>
          <h1 className="font-heading text-xl font-semibold tracking-normal sm:text-2xl">
            News timeline
          </h1>
          <p className="mt-1 text-sm leading-5 text-muted-foreground">
            Follow each story as a sequence of incidents, from the first
            reported event through the latest update.
          </p>
        </div>

        <div className="border-b" />
      </div>

      <div className="grid gap-4">
        {timelineStories.map((item) => (
          <Card
            key={item.id}
            className="rounded-sm border-l-2 border-l-primary/70 bg-muted/20"
          >
            <section>
              <CardHeader className="gap-2 pb-2 pt-3 px-4">
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="flex size-6 items-center justify-center rounded-md border bg-background text-primary">
                    <Newspaper className="size-3" />
                  </span>
                  <Badge variant="outline" className="text-xs px-1.5 py-0">
                    {item.focus_area?.[0] ?? "General"}
                  </Badge>
                  {item.is_trending && (
                    <Badge variant="secondary" className="text-xs px-1.5 py-0">
                      Trending
                    </Badge>
                  )}
                  <span className="rounded bg-background px-1.5 py-0.5 text-xs text-muted-foreground ring-1 ring-border">
                    {item.published_at
                      ? new Date(item.published_at).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })
                      : "—"}
                  </span>
                </div>
                <CardTitle className="max-w-4xl text-base leading-5 sm:text-lg">
                  {item.title ?? "Untitled"}
                </CardTitle>
              </CardHeader>

              <CardContent className="px-4 pb-3 text-sm leading-5 text-muted-foreground">
                <p className="max-w-4xl text-xs">
                  {item.short_summary ?? "No summary available."}
                </p>
              </CardContent>

              <CardFooter className="px-4 pb-3">
                <Link
                  href={`/timeline/${item.slug ?? item.id}`}
                  className="inline-flex items-center gap-1 text-xs font-medium text-primary transition-colors hover:text-primary/80"
                >
                  Read story
                  <ArrowUpRight className="size-3 transition-transform hover:-translate-y-0.5 hover:translate-x-0.5" />
                </Link>
              </CardFooter>
            </section>
          </Card>
        ))}

        {timelineStories.length === 0 && (
          <Card className="rounded-sm">
            <CardHeader>
              <CardTitle>No timeline stories yet</CardTitle>
            </CardHeader>
            <CardContent className="text-sm leading-6 text-muted-foreground">
              Stories will appear here once the pipeline has ingested articles.
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  )
}
