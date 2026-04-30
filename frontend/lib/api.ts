export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// ─── Types matching the backend PascalCase schema exactly ────────────────────

/** Lightweight shape returned by GET /posts (paginated list) */
export interface PostSummary {
  Id: number;
  Title: string | null;
  Short_Summary: string | null;
  Date: string | null;         // ISO datetime string
  Focus_Area: string | null;
  Image_Url: string[] | null;
}

/** Full shape returned by GET /posts/{id} */
export interface PostDetail extends PostSummary {
  Content_Length: number | null;
  Source_Url: string | null;
  Tags: string | null;
  Background: string | null;
  News: string | null;
  Highlights: string | null;
  Impact: string | null;
  Whats_Next: string | null;
  Overview: string | null;
  Impacts: string | null;
}

export interface PaginatedPosts {
  posts: PostSummary[];
  total: number;
  page: number;
}

// ─── Legacy interface kept for admin pages that still use it ─────────────────
export interface Post {
  id: string;
  title: string;
  slug: string;
  summary: string;
  content: string;
  cover_image?: string;
  tags: string[];
  category: string;
  source_urls: string[];
  created_at: string;
  updated_at: string;
  view_count?: number;
}

export interface AnalyticsOverview {
  total_posts: number;
  total_views: number;
  top_post: Post | null;
  top_tag: string | null;
}

// ─── Public post API ──────────────────────────────────────────────────────────

export async function getPosts(params?: {
  page?: number;
  limit?: number;
  focus_area?: string;
}): Promise<PaginatedPosts> {
  const url = new URL(`${API_URL}/posts`);
  if (params) {
    if (params.page)       url.searchParams.set("page",       params.page.toString());
    if (params.limit)      url.searchParams.set("limit",      params.limit.toString());
    if (params.focus_area) url.searchParams.set("focus_area", params.focus_area);
  }

  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) {
    throw new Error(`Failed to fetch posts: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getPostById(id: number): Promise<PostDetail | null> {
  const res = await fetch(`${API_URL}/posts/${id}`, { next: { revalidate: 60 } });
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error(`Failed to fetch post ${id}: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function searchPosts(q: string): Promise<PaginatedPosts> {
  const url = new URL(`${API_URL}/posts/search`);
  url.searchParams.set("q", q);
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Search failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// ─── Admin API ────────────────────────────────────────────────────────────────

function getHeaders(cookieStr?: string) {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (cookieStr) headers["Cookie"] = cookieStr;
  return headers;
}

export async function getAdminPosts(cookieStr?: string): Promise<{ posts: Post[]; total: number }> {
  const res = await fetch(`${API_URL}/admin/posts`, {
    headers: getHeaders(cookieStr),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch admin posts");
  return res.json();
}

export async function getAdminAnalytics(cookieStr?: string): Promise<AnalyticsOverview> {
  const res = await fetch(`${API_URL}/admin/analytics/overview`, {
    headers: getHeaders(cookieStr),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch analytics");
  return res.json();
}

export async function deletePost(id: string, cookieStr?: string): Promise<void> {
  const res = await fetch(`${API_URL}/admin/posts/${id}`, {
    method: "DELETE",
    headers: getHeaders(cookieStr),
  });
  if (!res.ok) throw new Error("Failed to delete post");
}
