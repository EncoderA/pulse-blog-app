import type React from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  CircleDot,
  ClipboardList,
  Clock3,
  Flag,
  Lightbulb,
  Rocket,
  Sparkles,
  Target,
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
import { getTimelinePost } from "@/lib/api";

const PLACEHOLDER = "Analysis coming soon.";

export default async function TimelineDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const post = await getTimelinePost(id);

  if (!post) {
    notFound();
  }

  const readTime = `${Math.ceil((post.events.reduce((acc, e) => acc + (e.event_content?.length ?? 0), 0) || 800) / 800)} min read`;

  const keyHighlightPoints = post.key_highlights
    ? post.key_highlights.split("\n").filter(Boolean)
    : [];

  const quickTakeItems = [
    {
      title: "What Happened?",
      description: post.what_happened ?? PLACEHOLDER,
      icon: Sparkles,
    },
    {
      title: "Why It Matters?",
      description: post.impact ?? PLACEHOLDER,
      icon: Lightbulb,
    },
    {
      title: "What's Next?",
      description: post.whats_next ?? PLACEHOLDER,
      icon: Rocket,
    },
  ];

  const articleSections = [
    { title: "Background", body: post.background ?? PLACEHOLDER, points: undefined },
    { title: "What Happened?", body: post.what_happened ?? PLACEHOLDER, points: undefined },
    ...(keyHighlightPoints.length > 0
      ? [{ title: "Key Highlights", body: undefined, points: keyHighlightPoints }]
      : [{ title: "Key Highlights", body: PLACEHOLDER, points: undefined }]),
    { title: "Impact", body: post.impact ?? PLACEHOLDER, points: undefined },
    { title: "What's Next?", body: post.whats_next ?? PLACEHOLDER, points: undefined },
  ];

  const keyFacts = [
    {
      label: "Focus Areas",
      value: post.focus_area?.join(", ") || "—",
      icon: Target,
    },
    {
      label: "Overview",
      value: post.overview ?? "—",
      icon: Flag,
    },
    {
      label: "Implementation",
      value: post.impacts_detail ?? "—",
      icon: ClipboardList,
    },
  ];

  const featuredQuote = post.quotes[0] ?? null;

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
                {post.title ?? "Untitled"}
              </h1>
              <p className="max-w-3xl text-base leading-7 text-muted-foreground sm:text-lg">
                {post.short_summary ?? "No summary available."}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
              <span className="inline-flex items-center gap-1.5">
                <CalendarDays className="size-4 text-primary" />
                {post.published_at
                  ? new Date(post.published_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })
                  : "—"}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Clock3 className="size-4 text-primary" />
                {readTime}
              </span>
              <Badge variant="secondary">
                {post.focus_area?.[0] ?? "General"}
              </Badge>
            </div>
          </header>

          <Separator />

          {/* Quick Take */}
          <section className="space-y-4">
            <h2 className="font-heading text-xl font-semibold tracking-normal text-foreground">
              Quick Take
            </h2>
            <div className="grid gap-4 sm:grid-cols-3">
              {quickTakeItems.map(({ title, description, icon: Icon }) => (
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

          {/* Story Timeline (events) */}
          {post.events.length > 0 && (
            <>
              <section className="space-y-6">
                <h2 className="font-heading text-xl font-semibold tracking-normal text-foreground">
                  Story Timeline
                </h2>
                <ol className="grid gap-4">
                  {post.events.map((event, index) => (
                    <li
                      key={event.id}
                      className="relative pl-14"
                    >
                      {/* Connector line */}
                      {index < post.events.length - 1 && (
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
                            {event.event_time
                              ? new Date(event.event_time).toLocaleDateString("en-US", {
                                  month: "short",
                                  day: "numeric",
                                  year: "numeric",
                                })
                              : "—"}
                          </span>
                          <span className="text-xs font-medium text-muted-foreground">
                            Incident {String(index + 1).padStart(2, "0")}
                          </span>
                        </div>
                        <h3 className="text-sm font-semibold text-foreground">
                          {event.event_title ?? "—"}
                        </h3>
                        <p className="mt-1 text-sm leading-6 text-muted-foreground">
                          {event.event_content ?? ""}
                        </p>
                      </div>
                    </li>
                  ))}
                </ol>
              </section>

              <Separator />
            </>
          )}

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

          {/* Featured quote */}
          {featuredQuote && (
            <>
              <Separator />
              <blockquote className="flex gap-5 border-l-4 border-primary pl-6">
                <div className="space-y-3">
                  <p className="text-xl font-medium leading-8 text-foreground">
                    &quot;{featuredQuote.quote_text}&quot;
                  </p>
                  {featuredQuote.attributed_to && (
                    <footer>
                      <p className="font-semibold text-foreground">
                        {featuredQuote.attributed_to}
                      </p>
                    </footer>
                  )}
                </div>
              </blockquote>
            </>
          )}
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
          {post.quotes.length > 0 && (
            <Card>
              <CardHeader className="border-b">
                <CardTitle className="text-base font-semibold">Top Quotes</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                {post.quotes.map((quote) => (
                  <blockquote
                    key={quote.id}
                    className="rounded-xl bg-muted/40 p-4 ring-1 ring-border"
                  >
                    <p className="text-sm leading-6 text-card-foreground">
                      &quot;{quote.quote_text}&quot;
                    </p>
                    {quote.attributed_to && (
                      <footer className="mt-3">
                        <p className="text-sm font-semibold text-card-foreground">
                          {quote.attributed_to}
                        </p>
                      </footer>
                    )}
                  </blockquote>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Source */}
          {post.source_url && (
            <Card>
              <CardHeader className="border-b">
                <CardTitle className="text-base font-semibold">Source</CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <a
                  href={post.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary underline-offset-4 hover:underline"
                >
                  Read original article
                </a>
              </CardContent>
            </Card>
          )}
        </aside>
      </div>
    </article>
  );
}
