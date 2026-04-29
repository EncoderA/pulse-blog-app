export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

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
  view_count?: number; // for analytics top posts
}

export interface PaginatedPosts {
  posts: Post[];
  total: number;
  page: number;
}

export interface AnalyticsOverview {
  total_posts: number;
  total_views: number;
  top_post: Post | null;
  top_tag: string | null;
}

export async function getPosts(params?: { page?: number; limit?: number; tag?: string; category?: string }): Promise<PaginatedPosts> {
  const url = new URL(`${API_URL}/posts`);
  if (params) {
    if (params.page) url.searchParams.append("page", params.page.toString());
    if (params.limit) url.searchParams.append("limit", params.limit.toString());
    if (params.tag) url.searchParams.append("tag", params.tag);
    if (params.category) url.searchParams.append("category", params.category);
  }

  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) {
    throw new Error("Failed to fetch posts");
  }
  return res.json();
}

export async function getPost(slug: string): Promise<Post | null> {
  const res = await fetch(`${API_URL}/posts/${slug}`, { next: { revalidate: 60 } });
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error(`Failed to fetch post: ${res.statusText}`);
  }
  return res.json();
}

// Helper to construct headers with cookie if provided
function getHeaders(cookieStr?: string) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (cookieStr) {
    headers["Cookie"] = cookieStr;
  }
  return headers;
}

export async function getAdminPosts(cookieStr?: string): Promise<{ posts: Post[], total: number }> {
  const res = await fetch(`${API_URL}/admin/posts`, {
    headers: getHeaders(cookieStr),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch admin posts");
  }
  return res.json();
}

export async function getAdminAnalytics(cookieStr?: string): Promise<AnalyticsOverview> {
  const res = await fetch(`${API_URL}/admin/analytics/overview`, {
    headers: getHeaders(cookieStr),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch analytics");
  }
  return res.json();
}

export async function deletePost(id: string, cookieStr?: string): Promise<void> {
  const res = await fetch(`${API_URL}/admin/posts/${id}`, {
    method: "DELETE",
    headers: getHeaders(cookieStr),
  });
  if (!res.ok) {
    throw new Error("Failed to delete post");
  }
}
