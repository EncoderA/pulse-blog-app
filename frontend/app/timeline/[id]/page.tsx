import type React from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  CircleDot,
  Clock3,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { getNewsItem, newsItems } from "@/lib/news";
import {
  quickTake,
  articleSections,
  keyFacts,
  topQuotes,
  relatedTopics,
  relatedArticles,
} from "@/lib/news-detail";

export function generateStaticParams() {
  return newsItems.map((item) => ({ id: item.id }));
}

export default async function TimelineDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const item = getNewsItem(id);

  if (!item) {
    notFound();
  }

  const sortedTimeline = [...item.timeline].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  return (
    <article className="min-h-screen w-full bg-background px-4 py-8 text-foreground sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[minmax(0,7fr)_minmax(280px,3fr)]">

        {/* ── Main column ── */}
        <main className="min-w-0 space-y-10">

          {/* Back link */}
          <Link
            href="/timeline"
            className={cn(
              buttonVariants({ variant: "ghost", size: "sm" }),
              "-ml-2 text-muted-foreground"
            )}
          >
            <ArrowLeft className="size-4" />
            Back to timeline
          </Link>

          {/* Hero / article header */}
          <header className="space-y-5">
            <div className="space-y-4">
              <h1 className="font-heading text-3xl font-bold leading-tight tracking-normal text-foreground sm:text-5xl">
                {item.title}
              </h1>
              <p className="max-w-3xl text-base leading-7 text-muted-foreground sm:text-lg">
                {item.excerpt}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
              <span className="inline-flex items-center gap-1.5">
                <CalendarDays className="size-4 text-primary" />
                {item.date}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Clock3 className="size-4 text-primary" />
                {item.readTime}
              </span>
              <Badge variant="secondary">{item.category}</Badge>
            </div>
          </header>

          <Separator />

          {/* Quick Take */}
          <section className="space-y-4">
            <h2 className="font-heading text-xl font-semibold tracking-normal text-foreground">
              Quick Take
            </h2>
            <div className="grid gap-4 sm:grid-cols-3">
              {quickTake.map(({ title, description, icon: Icon }) => (
                <div
                  key={title}
                  className="space-y-3 rounded-xl bg-muted/50 p-5 ring-1 ring-border transition duration-200 hover:bg-accent hover:shadow-sm"
                >
                  <div className="flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
                    <Icon className="size-5" />
                  </div>
                  <div>
                    <h3 className="font-heading text-sm font-semibold text-foreground">
                      {title}
                    </h3>
                    <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                      {description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <Separator />

          {/* Timeline */}
          <section className="space-y-6">
            <h2 className="font-heading text-xl font-semibold tracking-normal text-foreground">
              Story Timeline
            </h2>
            <ol className="grid gap-4">
              {sortedTimeline.map((event, index) => (
                <li
                  key={`${event.date}-${event.title}`}
                  className="relative pl-14"
                >
                  {/* Connector line */}
                  {index < sortedTimeline.length - 1 && (
                    <div className="absolute bottom-[-1.25rem] left-5 top-10 w-px bg-border" />
                  )}
                  {/* Icon */}
                  <div className="absolute left-0 top-4 z-10 flex size-10 items-center justify-center rounded-full border bg-background text-primary shadow-sm">
                    <CircleDot className="size-4" />
                  </div>
                  {/* Event card */}
                  <div className="rounded-xl bg-muted/40 p-4 ring-1 ring-border">
                    <div className="mb-2 flex flex-wrap items-center gap-2">
                      <span className="rounded-md bg-background px-2 py-0.5 text-xs font-medium text-muted-foreground ring-1 ring-border">
                        {event.date}
                      </span>
                      <span className="text-xs font-medium text-muted-foreground">
                        Incident {String(index + 1).padStart(2, "0")}
                      </span>
                    </div>
                    <h3 className="text-sm font-semibold text-foreground">
                      {event.title}
                    </h3>
                    <p className="mt-1 text-sm leading-6 text-muted-foreground">
                      {event.description}
                    </p>
                  </div>
                </li>
              ))}
            </ol>
          </section>

          <Separator />

          {/* Article body */}
          <section className="space-y-8">
            {articleSections.map((s) => (
              <div key={s.title} className="space-y-3">
                <h2 className="font-heading text-2xl font-semibold tracking-normal text-foreground">
                  {s.title}
                </h2>
                {s.points ? (
                  <ul className="space-y-3 text-base leading-8 text-muted-foreground">
                    {s.points.map((point) => (
                      <li key={point} className="flex gap-3">
                        <CheckCircle2 className="mt-1 size-5 shrink-0 text-primary" />
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-base leading-8 text-muted-foreground">
                    {s.body}
                  </p>
                )}
              </div>
            ))}
          </section>

          <Separator />

          {/* Featured quote */}
          <blockquote className="flex gap-5 border-l-4 border-primary pl-6">
            <div className="space-y-3">
              <p className="text-xl font-medium leading-8 text-foreground">
                &quot;Artificial intelligence must become a force multiplier for
                every citizen, every startup, and every public service.&quot;
              </p>
              <footer>
                <p className="font-semibold text-foreground">Narendra Modi</p>
                <p className="text-sm text-muted-foreground">
                  Prime Minister of India
                </p>
              </footer>
            </div>
          </blockquote>
        </main>

        {/* ── Sidebar ── */}
        <aside className="space-y-5 lg:sticky lg:top-6 lg:self-start">

          {/* Key Facts */}
          <Card>
            <CardHeader className="border-b">
              <CardTitle className="text-base font-semibold">Key Facts</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              {keyFacts.map(({ label, value, icon: Icon }) => (
                <div key={label} className="flex gap-3">
                  <div className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                    <Icon className="size-4" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-card-foreground">{label}</p>
                    <p className="text-sm leading-6 text-muted-foreground">{value}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Top Quotes */}
          <Card>
            <CardHeader className="border-b">
              <CardTitle className="text-base font-semibold">Top Quotes</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              {topQuotes.map((quote) => (
                <blockquote
                  key={quote.author}
                  className="rounded-xl bg-muted/40 p-4 ring-1 ring-border"
                >
                  <p className="text-sm leading-6 text-card-foreground">
                    &quot;{quote.text}&quot;
                  </p>
                  <footer className="mt-3">
                    <p className="text-sm font-semibold text-card-foreground">{quote.author}</p>
                    <p className="text-xs text-muted-foreground">{quote.designation}</p>
                  </footer>
                </blockquote>
              ))}
            </CardContent>
          </Card>

          {/* Related Topics */}
          <Card>
            <CardHeader className="border-b">
              <CardTitle className="text-base font-semibold">Related Topics</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2 pt-4">
              {relatedTopics.map((topic) => (
                <Badge
                  key={topic.name}
                  variant="outline"
                  className="transition hover:bg-accent hover:text-accent-foreground"
                >
                  {topic.name} · {topic.count}
                </Badge>
              ))}
            </CardContent>
          </Card>

          {/* You May Also Like */}
          <Card>
            <CardHeader className="border-b">
              <CardTitle className="text-base font-semibold">You May Also Like</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 pt-4">
              {relatedArticles.map((article) => (
                <Link
                  key={article.title}
                  href="/timeline"
                  className="group flex gap-3 rounded-lg p-2 transition hover:bg-accent"
                >
                  <div
                    className={`flex size-14 shrink-0 items-center justify-center rounded-lg ${article.thumbnail} shadow-sm`}
                  >
                    <article.icon className="size-5" />
                  </div>
                  <div className="min-w-0">
                    <p className="line-clamp-2 text-sm font-semibold leading-5 text-card-foreground transition group-hover:text-accent-foreground">
                      {article.title}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">{article.date}</p>
                  </div>
                </Link>
              ))}
            </CardContent>
          </Card>
        </aside>
      </div>
    </article>
  );
}
