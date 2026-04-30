const analyticsUrl =
  process.env.NEXT_PUBLIC_ANALYTICS_URL ?? "http://localhost:4005";

export default function AnalyticsPage() {
  return (
    <main className="flex w-full flex-1 flex-col">
      <div className="border-b px-4 py-4 sm:px-6 lg:px-8">
        <h1 className="font-heading text-xl font-semibold tracking-normal">
          Analytics
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Scraper performance — articles ingested per source, trends, and growth.
        </p>
      </div>
      <iframe
        src={analyticsUrl}
        title="Analytics Dashboard"
        className="w-full flex-1 border-none"
        style={{ minHeight: "calc(100vh - 120px)" }}
      />
    </main>
  );
}
