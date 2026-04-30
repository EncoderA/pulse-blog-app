import Link from "next/link"
import { ArrowUpRight, CircleDot, Newspaper } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { newsItems } from "@/lib/news"

function getTime(date: string) {
  return new Date(date).getTime()
}

export default function TimelinePage() {
  const timelineStories = [...newsItems].sort((first, second) => {
    return getTime(second.date) - getTime(first.date)
  })

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
        {timelineStories.map((item) => {
          const incidents = [...item.timeline].sort((first, second) => {
            return getTime(first.date) - getTime(second.date)
          })

          return (
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
                    <Badge variant="outline" className="text-xs px-1.5 py-0">{item.category}</Badge>
                    <span className="rounded bg-background px-1.5 py-0.5 text-xs text-muted-foreground ring-1 ring-border">
                      Updated {item.date}
                    </span>
                  </div>
                  <CardTitle className="max-w-4xl text-base leading-5 sm:text-lg">
                    {item.title}
                  </CardTitle>
                </CardHeader>

                <CardContent className="grid gap-3 px-4 pb-3 text-sm leading-5 text-muted-foreground">
                  <p className="max-w-4xl text-xs">{item.excerpt}</p>

                  <ol className="grid gap-3">
                    {incidents.map((event, index) => (
                      <li
                        key={`${item.id}-${event.date}-${event.title}`}
                        className="relative pl-10"
                      >
                        {index < incidents.length - 1 && (
                          <div className="absolute bottom-[-2.75rem] left-3.5 top-8 w-px bg-border" />
                        )}
                        <div className="absolute left-0 top-3 z-10 flex size-7 items-center justify-center rounded-full border bg-background text-primary shadow-sm">
                          <CircleDot className="size-3" />
                        </div>
                        <Link
                          href={`/timeline/${item.id}`}
                          aria-label={`Read ${item.title}: ${event.title}`}
                          className="group block rounded-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                        >
                          <Card className="rounded-sm border-border/80 bg-background transition-colors group-hover:border-primary/50 group-hover:bg-muted/30">
                            <CardContent className="grid gap-1.5 p-3">
                              <div className="flex flex-wrap items-center gap-1.5">
                                <span className="rounded bg-muted px-1.5 py-0.5 text-xs font-medium text-muted-foreground">
                                  {event.date}
                                </span>
                                <span className="text-xs font-medium text-muted-foreground">
                                  Incident {String(index + 1).padStart(2, "0")}
                                </span>
                              </div>
                              <h3 className="text-sm font-semibold leading-5 text-foreground">
                                {event.title}
                              </h3>
                              <p className="max-w-3xl text-xs leading-5 text-muted-foreground">
                                {event.description}
                              </p>
                            </CardContent>
                            <CardFooter className="px-3 py-2 pt-0">
                              <span className="inline-flex items-center gap-1 text-xs font-medium text-primary transition-colors group-hover:text-primary/80">
                                Read story
                                <ArrowUpRight className="size-3 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
                              </span>
                            </CardFooter>
                          </Card>
                        </Link>
                      </li>
                    ))}
                  </ol>
                </CardContent>
              </section>
            </Card>
          )
        })}
      </div>
    </main>
  )
}
