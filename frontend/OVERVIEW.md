# Frontend App Overview

## Purpose
`frontend` is the user-facing web UI built with Next.js. It provides public news browsing, timeline/detail views, and an admin-style dashboard UI.

## Tech Stack
- Next.js (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui components

## Main Responsibilities
- Route users:
  - `/` redirects to `/news`
  - `/news` list + filter view
  - `/news/[id]` detail pages
  - `/timeline` and `/timeline/[id]`
  - `/admin` editorial dashboard UI
- Render article cards, detail content, and timeline blocks
- Provide client/server helper APIs in `lib/api.ts` for backend integration

## Data Pattern in Current Code
- UI pages currently rely heavily on local static data (`lib/news.ts`, `lib/news-detail.ts`).
- API helper module exists (`lib/api.ts`) and points to `NEXT_PUBLIC_API_URL`, but several UI routes are not fully wired to backend responses yet.

## Runtime Flow (Current)
1. User opens app and lands on `/news`.
2. News listing filters locally by category.
3. Detail/admin pages render from in-repo static data.
4. Optional API integration functions are available for future/partial backend wiring.

## Current Status Notes
- Frontend appears to be in a transition state between static mock data and live backend-backed data.
