import { NextRequest, NextResponse } from "next/server";
import { mapPostSummary } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

/**
 * GET /api/search?q=<query>
 *
 * Proxies to GET /posts/search?q=<query> on the FastAPI backend.
 * Running server-side avoids CORS entirely — the browser only ever
 * talks to the same Next.js origin.
 */
export async function GET(request: NextRequest) {
  const q = request.nextUrl.searchParams.get("q");

  if (!q || !q.trim()) {
    return NextResponse.json({ posts: [], total: 0 }, { status: 200 });
  }

  try {
    const upstream = new URL(`${API_URL}/posts/search`);
    upstream.searchParams.set("q", q.trim());

    const res = await fetch(upstream.toString(), {
      // never cache search results
      cache: "no-store",
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: `Upstream error: ${res.status} ${res.statusText}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json({
      ...data,
      posts: data.posts.map(mapPostSummary)
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json(
      { error: `Failed to reach search API: ${message}` },
      { status: 502 }
    );
  }
}
