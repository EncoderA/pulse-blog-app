import type React from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  CalendarDays,
  Clock3,
  FileText,
  Globe,
  Tag,
  CheckCircle2,
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
import { getPostById } from "@/lib/api";
import { BlogVisitTracker } from "@/components/blog-visit-tracker";
import {
  quickTake,
  keyFacts,
  topQuotes,
  relatedTopics,
  relatedArticles,
} from "@/lib/news-detail";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "";
  try {
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

/** Rough read-time estimate: ~200 words / minute */
function estimateReadTime(contentLength: number | null): string {
  if (!contentLength) return "";
  const minutes = Math.max(1, Math.round(contentLength / 1000));
  return `${minutes} min read`;
}

/** Split a pipe-separated or comma-separated tags string */
function parseTags(tags: string | null): string[] {
  if (!tags) return [];
  return tags
    .split(/[|,]/)
    .map((t) => t.trim())
    .filter(Boolean);
}

/** Split a multi-sentence field into a bullet list */
function splitSentences(text: string | null): string[] {
  if (!text) return [];
  return text
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

// ─── Article section helper ───────────────────────────────────────────────────

function ArticleSection({
  title,
  text,
  asBullets = false,
}: {
  title: string;
  text: string | null;
  asBullets?: boolean;
}) {
  if (!text) return null;
  const points = asBullets ? splitSentences(text) : null;

  return (
    <div className="space-y-3">
      <h2 className="font-heading text-2xl font-semibold tracking-normal text-foreground">
        {title}
      </h2>
      {points ? (
        <ul className="space-y-3 text-base leading-8 text-muted-foreground">
          {points.map((point, i) => (
            <li key={i} className="flex gap-3">
              <CheckCircle2 className="mt-1 size-5 shrink-0 text-primary" />
              <span>{point}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-base leading-8 text-muted-foreground">{text}</p>
      )}
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default async function NewsDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Guard: id must be a positive integer
  const numericId = parseInt(id, 10);
  if (isNaN(numericId) || numericId <= 0) {
    notFound();
  }

  const post = await getPostById(numericId).catch(() => null);
  if (!post) notFound();

  const tags = parseTags(post.Tags);
  const readTime = estimateReadTime(post.Content_Length);

  // Build article sections from real fields — skip nulls automatically
  const sections: Array<{ title: string; text: string | null; asBullets?: boolean }> = [
    { title: "Overview", text: post.Overview },
    { title: "Background", text: post.Background },
    { title: "News", text: post.News },
    { title: "Highlights", text: post.Highlights, asBullets: true },
    { title: "Impact", text: post.Impact },
    { title: "Impacts", text: post.Impacts, asBullets: true },
    { title: "What's Next", text: post.Whats_Next },
  ];

  return (
    <>
      {/* Analytics tracker — client component, fire-and-forget */}
      <BlogVisitTracker id={numericId} />

      <article className="min-h-screen w-full bg-background px-4 py-8 text-foreground sm:px-6 lg:px-8">
        <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[minmax(0,7fr)_minmax(280px,3fr)]">

          {/* ── Main column ── */}
          <main className="min-w-0 space-y-10">

            {/* Back link */}
            <Link
              href="/news"
              className={cn(
                buttonVariants({ variant: "ghost", size: "sm" }),
                "-ml-2 text-muted-foreground"
              )}
            >
              <ArrowLeft className="size-4" />
              Back to news
            </Link>

            {/* Hero */}
            <header className="space-y-5">
              {post.Focus_Area && (
                <Badge variant="secondary">{post.Focus_Area}</Badge>
              )}
              <div className="space-y-4">
                <h1 className="font-heading text-3xl font-bold leading-tight tracking-normal text-foreground sm:text-5xl">
                  {post.Title ?? "Untitled"}
                </h1>
                {post.Short_Summary && (
                  <p className="max-w-3xl text-base leading-7 text-muted-foreground sm:text-lg">
                    {post.Short_Summary}
                  </p>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                {post.Date && (
                  <span className="inline-flex items-center gap-1.5">
                    <CalendarDays className="size-4 text-primary" />
                    {formatDate(post.Date)}
                  </span>
                )}
                {readTime && (
                  <span className="inline-flex items-center gap-1.5">
                    <Clock3 className="size-4 text-primary" />
                    {readTime}
                  </span>
                )}
                {post.Source_Url && (
                  <a
                    href={post.Source_Url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-primary underline-offset-4 hover:underline"
                  >
                    <Globe className="size-4" />
                    Source
                  </a>
                )}
              </div>

              {/* Tags */}
              {tags.length > 0 && (
                <div className="flex flex-wrap items-center gap-2">
                  <Tag className="size-3.5 text-muted-foreground" />
                  {tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
            </header>

            <Separator />

            {/* Quick Take (static demo cards — kept from original design) */}
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

            {/* Dynamic article body from real API fields */}
            <section className="space-y-8">
              {sections.some((s) => s.text) ? (
                sections.map((s) => (
                  <ArticleSection
                    key={s.title}
                    title={s.title}
                    text={s.text}
                    asBullets={s.asBullets}
                  />
                ))
              ) : (
                <div className="flex items-center gap-2 rounded-xl bg-muted/40 p-5 text-sm text-muted-foreground ring-1 ring-border">
                  <FileText className="size-4 shrink-0" />
                  Full article content is not yet available for this story.
                </div>
              )}
            </section>

            {/* Featured quote (static) */}
            <Separator />
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
                      <p className="text-sm font-semibold text-card-foreground">
                        {quote.author}
                      </p>
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
                    href="/news"
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
    </>
  );
}
