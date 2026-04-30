import Link from "next/link";
import { ArrowUpRight, ChevronLeft, ChevronRight, AlertCircle, RefreshCw, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ComboboxMultiple } from "@/components/filter-multiselect";
import { getPosts, searchPosts, type PostSummary } from "@/lib/api";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";

const POSTS_PER_PAGE = 10;

type NewsSearchParams = {
  category?: string | string[];
  page?: string;
  q?: string;
};

function allParams(value: string | string[] | undefined): string[] {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "";
  try {
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

// ─── Pagination bar ───────────────────────────────────────────────────────────

function PaginationBar({
  currentPage,
  totalPages,
  focusArea,
}: {
  currentPage: number;
  totalPages: number;
  focusArea: string[];
}) {
  if (totalPages <= 1) return null;

  function buildHref(page: number) {
    const params = new URLSearchParams();
    focusArea.forEach((f) => params.append("category", f));
    params.set("page", page.toString());
    return `/news?${params.toString()}`;
  }

  return (
    <nav
      aria-label="Pagination"
      className="mt-6 flex items-center justify-between gap-4 border-t pt-6"
    >
      <Link
        href={buildHref(currentPage - 1)}
        aria-disabled={currentPage <= 1}
        className={cn(
          buttonVariants({ variant: "outline", size: "sm" }),
          currentPage <= 1 && "pointer-events-none opacity-40"
        )}
      >
        <ChevronLeft className="size-4" />
        Previous
      </Link>

      <span className="text-sm text-muted-foreground">
        Page {currentPage} of {totalPages}
      </span>

      <Link
        href={buildHref(currentPage + 1)}
        aria-disabled={currentPage >= totalPages}
        className={cn(
          buttonVariants({ variant: "outline", size: "sm" }),
          currentPage >= totalPages && "pointer-events-none opacity-40"
        )}
      >
        Next
        <ChevronRight className="size-4" />
      </Link>
    </nav>
  );
}

// ─── Error card ───────────────────────────────────────────────────────────────

function ErrorCard({ message }: { message: string }) {
  return (
    <Card className="rounded-sm border-destructive/40 bg-destructive/5">
      <CardHeader>
        <div className="flex items-center gap-2">
          <AlertCircle className="size-5 text-destructive" />
          <CardTitle className="text-base text-destructive">
            Could not load stories
          </CardTitle>
        </div>
      </CardHeader>
      <CardContent className="text-sm leading-6 text-muted-foreground">
        {message}
      </CardContent>
      <CardFooter>
        <Link
          href="/news"
          className={cn(
            buttonVariants({ variant: "outline", size: "sm" }),
            "gap-1.5"
          )}
        >
          <RefreshCw className="size-3.5" />
          Retry
        </Link>
      </CardFooter>
    </Card>
  );
}

// ─── Post card ────────────────────────────────────────────────────────────────

function PostCard({ post }: { post: PostSummary }) {
  return (
    <Card key={post.Id} className="min-h-32 rounded-sm">
      <CardHeader>
        <div className="mb-2 flex items-center justify-between gap-3">
          {post.Focus_Area ? (
            <Badge variant="outline">{post.Focus_Area}</Badge>
          ) : (
            <span />
          )}
          <span className="text-xs text-muted-foreground">
            {formatDate(post.Date)}
          </span>
        </div>
        <CardTitle className="line-clamp-2">{post.Title ?? "Untitled"}</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 text-sm leading-6 text-muted-foreground line-clamp-3">
        {post.Short_Summary ?? ""}
      </CardContent>
      <CardFooter>
        <Link
          href={`/news/${post.Id}`}
          className="inline-flex items-center gap-1 text-sm font-medium text-primary"
        >
          Read story
          <ArrowUpRight className="size-3.5" />
        </Link>
      </CardFooter>
    </Card>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default async function NewsPage({
  searchParams,
}: {
  searchParams: Promise<NewsSearchParams>;
}) {
  const params = await searchParams;
  const activeCategories = allParams(params.category);
  const currentPage = Math.max(1, parseInt(params.page ?? "1", 10) || 1);
  const searchQuery = params.q?.trim() ?? "";
  const isSearchMode = searchQuery.length > 0;

  // Fetch from the real FastAPI backend
  let posts: PostSummary[] = [];
  let total = 0;
  let fetchError: string | null = null;

  try {
    if (isSearchMode) {
      // Search mode: hit GET /posts/search?q=
      const data = await searchPosts(searchQuery);
      posts = data.posts;
      total = data.total;
    } else {
      // Browse mode: hit GET /posts with pagination + focus_area filter
      const data = await getPosts({
        page: currentPage,
        limit: POSTS_PER_PAGE,
        focus_area: activeCategories[0],
      });
      posts = data.posts;
      total = data.total;
    }
  } catch (err) {
    fetchError =
      err instanceof Error
        ? err.message
        : "An unexpected error occurred while fetching stories.";
  }

  // Derive available focus areas from this page's results
  const categories = Array.from(
    new Set(posts.map((p) => p.Focus_Area).filter(Boolean) as string[])
  ).sort();

  const totalPages = Math.max(1, Math.ceil(total / POSTS_PER_PAGE));

  return (
    <div className="flex w-full flex-1 flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-2xl">
            <Badge variant="secondary" className="mb-4">
              {isSearchMode ? "Search results" : "News"}
            </Badge>
            <h1 className="font-heading text-3xl font-semibold tracking-normal sm:text-4xl">
              {isSearchMode ? `Results for "${searchQuery}"` : "Latest updates"}
            </h1>
            <p className="mt-3 text-base leading-7 text-muted-foreground">
              {isSearchMode
                ? `${total} ${total === 1 ? "story" : "stories"} matched your search.`
                : "Browse current Pulse stories across business, policy, entertainment, and community coverage."}
            </p>
          </div>

          <div className="flex flex-col items-end gap-3">
            {isSearchMode ? (
              <Link
                href="/news"
                className={cn(
                  buttonVariants({ variant: "outline", size: "sm" }),
                  "gap-1.5"
                )}
              >
                <X className="size-3.5" />
                Clear search
              </Link>
            ) : (
              <ComboboxMultiple
                items={categories}
                selectedItems={activeCategories}
                resultCount={posts.length}
                totalCount={total}
              />
            )}
          </div>
        </div>

        <div className="border-b" />
      </div>

      <div className="grid gap-4">
        {fetchError ? (
          <ErrorCard message={fetchError} />
        ) : posts.length === 0 ? (
          <Card className="rounded-sm">
            <CardHeader>
              <CardTitle>No stories match these filters</CardTitle>
            </CardHeader>
            <CardContent className="text-sm leading-6 text-muted-foreground">
              Adjust the topic filter or browse without a filter to see all stories.
            </CardContent>
          </Card>
        ) : (
          posts.map((post) => <PostCard key={post.Id} post={post} />)
        )}
      </div>

      {/* Pagination: only show in browse mode, not in search mode */}
      {!fetchError && !isSearchMode && (
        <PaginationBar
          currentPage={currentPage}
          totalPages={totalPages}
          focusArea={activeCategories}
        />
      )}
    </div>
  );
}
