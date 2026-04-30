import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ComboboxMultiple } from "@/components/filter-multiselect";
import { API_URL } from "@/lib/api";

type BackendPostSummary = {
  Id: number;
  Title: string | null;
  Short_Summary: string | null;
  Date: string | null;
  Focus_Area: string | null;
};

type NewsSearchParams = {
  category?: string | string[];
};

function allParams(value: string | string[] | undefined) {
  if (!value) {
    return [];
  }

  return Array.isArray(value) ? value : [value];
}

export default async function NewsPage({
  searchParams,
}: {
  searchParams: Promise<NewsSearchParams>;
}) {
  const params = await searchParams;
  const activeCategories = allParams(params.category);
  const res = await fetch(`${API_URL}/posts?page=1&limit=100`, { cache: "no-store" });
  const data: { posts: BackendPostSummary[]; total: number; page: number } = res.ok
    ? await res.json()
    : { posts: [], total: 0, page: 1 };

  const categories = Array.from(
    new Set(data.posts.map((item) => item.Focus_Area).filter(Boolean) as string[])
  ).sort();

  const filteredItems = data.posts.filter((item) => {
    return (
      activeCategories.length === 0 ||
      (item.Focus_Area ? activeCategories.includes(item.Focus_Area) : false)
    );
  });

  return (
    <div className="flex w-full flex-1 flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-2xl">
            <Badge variant="secondary" className="mb-4">
              News
            </Badge>
            <h1 className="font-heading text-3xl font-semibold tracking-normal sm:text-4xl">
              Latest updates
            </h1>
            <p className="mt-3 text-base leading-7 text-muted-foreground">
              Browse current Pulse stories across business, policy, entertainment, and community coverage.
            </p>
          </div>
          <ComboboxMultiple
            items={categories}
            selectedItems={activeCategories}
            resultCount={filteredItems.length}
            totalCount={data.posts.length}
          />
        </div>

        <div className="border-b" />
      </div>

      <div className="grid gap-4">
        {filteredItems.map((item) => (
          <Card key={item.Id} className="min-h-32 rounded-sm">
            <CardHeader>
              <div className="mb-2 flex items-center justify-between gap-3">
                <Badge variant="outline">{item.Focus_Area || "General"}</Badge>
                <span className="text-xs text-muted-foreground">
                  {item.Date ? new Date(item.Date).toLocaleDateString() : "-"}
                </span>
              </div>
              <CardTitle>{item.Title || "Untitled"}</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 text-sm leading-6 text-muted-foreground">
              {item.Short_Summary || "No summary available."}
            </CardContent>
            <CardFooter>
              <Link
                href={`/news/${item.Id}`}
                className="inline-flex items-center gap-1 text-sm font-medium text-primary"
              >
                Read story
                <ArrowUpRight className="size-3.5" />
              </Link>
            </CardFooter>
          </Card>
        ))}
        {filteredItems.length === 0 && (
          <Card className="rounded-sm">
            <CardHeader>
              <CardTitle>No stories match these filters</CardTitle>
            </CardHeader>
            <CardContent className="text-sm leading-6 text-muted-foreground">
              Adjust the search text, topic, or status to broaden the results.
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
