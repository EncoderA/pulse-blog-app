export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// ─── Agent Config types ─────────────────────────────────────────────────────

export type AgentConfig = {
  id?: number
  context_name: string
  custom_instructions: string | null
  focus_topics: string[] | null
  tone: "neutral" | "analytical" | "simplified"
  analysis_depth: "brief" | "standard" | "deep"
  llm_model_override: string | null
  auto_enrich: boolean
  active: boolean
  created_at?: string | null
  updated_at?: string | null
}

export type EnrichmentStatus = {
  pending: number
  enriching: number
  enriched: number
  failed: number
  [key: string]: number
}

export async function getAgentConfig(): Promise<AgentConfig | null> {
  const res = await fetch(`${API_URL}/admin/agent-config`, { cache: "no-store" })
  if (!res.ok) return null
  return res.json()
}

export async function saveAgentConfig(payload: Omit<AgentConfig, "id" | "created_at" | "updated_at">): Promise<AgentConfig> {
  const res = await fetch(`${API_URL}/admin/agent-config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(`Failed to save agent config: ${res.statusText}`)
  return res.json()
}

export async function updateAgentConfig(id: number, payload: Partial<AgentConfig>): Promise<AgentConfig> {
  const res = await fetch(`${API_URL}/admin/agent-config/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(`Failed to update agent config: ${res.statusText}`)
  return res.json()
}

export async function getEnrichmentStatus(): Promise<EnrichmentStatus> {
  const res = await fetch(`${API_URL}/admin/enrichment/status`, { cache: "no-store" })
  if (!res.ok) return { pending: 0, enriching: 0, enriched: 0, failed: 0 }
  return res.json()
}

export async function retryFailedPosts(): Promise<{ reset: number }> {
  const res = await fetch(`${API_URL}/admin/enrichment/retry-failed`, { method: "POST" })
  if (!res.ok) throw new Error("Failed to retry posts")
  return res.json()
}

export async function runEnrichmentNow(): Promise<{ status: string }> {
  const res = await fetch(`${API_URL}/admin/enrichment/run`, { method: "POST" })
  if (!res.ok) throw new Error("Failed to trigger enrichment run")
  return res.json()
}

// ─── Timeline types ────────────────────────────────────────────────────────

export type TimelineEventOut = {
  id: number
  event_time: string | null
  event_title: string | null
  event_content: string | null
  event_image_url: string | null
  sequence_order: number
}

export type TimelineQuoteOut = {
  id: number
  quote_text: string
  attributed_to: string | null
}

export type TimelineCommentOut = {
  id: number
  comment_text: string
  commenter_name: string | null
  commenter_designation: string | null
  commenter_image_url: string | null
}

export type TimelinePostSummary = {
  id: number
  slug: string | null
  title: string | null
  short_summary: string | null
  published_at: string | null
  focus_area: string[] | null
  is_trending: boolean
  primary_image_url: string | null
  ingest_status: string | null
}

export type TimelinePostDetail = TimelinePostSummary & {
  quick_take: string | null
  background: string | null
  what_happened: string | null
  key_highlights: string | null
  impact: string | null
  whats_next: string | null
  overview: string | null
  impacts_detail: string | null
  source_url: string | null
  events: TimelineEventOut[]
  quotes: TimelineQuoteOut[]
  comments: TimelineCommentOut[]
}

export async function getTimelinePosts(): Promise<TimelinePostSummary[]> {
  const res = await fetch(`${API_URL}/timeline/posts`, { cache: "no-store" })
  if (!res.ok) return []
  return res.json()
}

export async function getTimelinePost(slug: string): Promise<TimelinePostDetail | null> {
  const res = await fetch(`${API_URL}/timeline/posts/${slug}`, { cache: "no-store" })
  if (!res.ok) {
    if (res.status === 404) return null
    throw new Error(`Failed to fetch timeline post: ${res.statusText}`)
  }
  return res.json()
}

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
