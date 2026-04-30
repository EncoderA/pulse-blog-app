"use client";

import { useEffect } from "react";
import { API_URL } from "@/lib/api";

/**
 * Fires a single POST /analytics/blog-visit/{id} on mount.
 * Rendered as a child of the (Server Component) detail page so the
 * page itself stays server-rendered.
 */
export function BlogVisitTracker({ id }: { id: string }) {
  useEffect(() => {
    fetch(`${API_URL}/analytics/blog-visit/${id}`, {
      method: "POST",
      // fire-and-forget — we don't need to await the result
    }).catch(() => {
      // swallow errors silently — analytics should never break the UX
    });
  }, [id]);

  return null;
}
