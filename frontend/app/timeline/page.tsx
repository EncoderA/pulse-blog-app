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
    <main className="mx-auto flex w-full flex-1 flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-6">
        <div className="max-w-3xl">
          <Badge variant="secondary" className="mb-4">
            Timeline
          </Badge>
          <h1 className="font-heading text-3xl font-semibold tracking-normal sm:text-4xl">
            News timeline
          </h1>
          <p className="mt-3 text-base leading-7 text-muted-foreground">
            Follow each story as a sequence of incidents, from the first
            reported event through the latest update.
          </p>
        </div>

        <div className="border-b" />
      </div>

      <div className="grid gap-8">
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
                <CardHeader className="gap-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="flex size-8 items-center justify-center rounded-lg border bg-background text-primary">
                      <Newspaper className="size-4" />
                    </span>
                    <Badge variant="outline">{item.category}</Badge>
                    <span className="rounded-md bg-background px-2 py-1 text-xs text-muted-foreground ring-1 ring-border">
                      Updated {item.date}
                    </span>
                  </div>
                  <CardTitle className="max-w-4xl text-xl leading-7 sm:text-2xl">
                    {item.title}
                  </CardTitle>
                </CardHeader>

                <CardContent className="grid gap-5 text-sm leading-6 text-muted-foreground">
                  <p className="max-w-4xl">{item.excerpt}</p>

                  <ol className="grid gap-4">
                    {incidents.map((event, index) => (
                      <li
                        key={`${item.id}-${event.date}-${event.title}`}
                        className="relative pl-14"
                      >
                        {index < incidents.length - 1 && (
                          <div className="absolute bottom-[-3.5rem] left-5 top-10 w-px bg-border" />
                        )}
                        <div className="absolute left-0 top-5 z-10 flex size-10 items-center justify-center rounded-full border bg-background text-primary shadow-sm">
                          <CircleDot className="size-4" />
                        </div>
                        <Link
                          href={`/news/${item.id}`}
                          aria-label={`Read ${item.title}: ${event.title}`}
                          className="group block rounded-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                        >
                          <Card className="rounded-sm border-border/80 bg-background transition-colors group-hover:border-primary/50 group-hover:bg-muted/30">
                            <CardContent className="grid gap-3 p-4 sm:p-5">
                              <div className="flex flex-wrap items-center gap-2">
                                <span className="rounded-md bg-muted px-2 py-1 text-xs font-medium text-muted-foreground">
                                  {event.date}
                                </span>
                                <span className="text-xs font-medium text-muted-foreground">
                                  Incident {String(index + 1).padStart(2, "0")}
                                </span>
                              </div>
                              <h3 className="text-base font-semibold leading-6 text-foreground">
                                {event.title}
                              </h3>
                              <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
                                {event.description}
                              </p>
                            </CardContent>
                            <CardFooter className="pt-0">
                              <span className="inline-flex items-center gap-1 text-sm font-medium text-primary transition-colors group-hover:text-primary/80">
                                Read story
                                <ArrowUpRight className="size-3.5 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
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
