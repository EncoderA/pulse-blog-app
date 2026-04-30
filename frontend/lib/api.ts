export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// ─── Types matching the backend schema exactly ────────────────────────────────
// Backend uses: id (UUID), title, slug, summary, content, cover_image,
//               source_urls (array), tags (array), category, status,
//               created_at, updated_at

/** Lightweight shape returned by GET /posts (paginated list) */
export interface PostSummary {
  id: string;           // UUID
  title: string;
  slug: string;
  summary: string;
  cover_image: string | null;
  tags: string[];
  category: string | null;
  created_at: string;   // ISO datetime
}

/** Full shape returned by GET /posts/{id} */
export interface PostDetail extends PostSummary {
  content: string;
  source_urls: string[];
  status: string;
  updated_at: string;
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
  category?: string;   // backend param name is "category"
}): Promise<PaginatedPosts> {
  const url = new URL(`${API_URL}/posts`);
  if (params) {
    if (params.page)     url.searchParams.set("page",     params.page.toString());
    if (params.limit)    url.searchParams.set("limit",    params.limit.toString());
    if (params.category) url.searchParams.set("category", params.category);
  }

  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) {
    throw new Error(`Failed to fetch posts: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

/** id is a UUID string, e.g. "3f2504e0-..." */
export async function getPostById(id: string): Promise<PostDetail | null> {
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
