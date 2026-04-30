import { useEffect, useState } from "react";
import {
  getScrapperAnalytics, getTrend,
  getComparison, getGrowth, refreshAnalytics,
} from "../api/analyticsApi";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell,
  LineChart, Line,
  ResponsiveContainer,
} from "recharts";

// suppress Cell deprecation — still works fine in recharts v2


const COLORS = ["#6366f1", "#0ea5e9", "#f59e0b", "#10b981", "#f43f5e", "#8b5cf6"];

// ── helpers ──────────────────────────────────────────────────────────────────

const CustomTooltip = ({ active, payload, label, dark }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className={`rounded-lg border px-4 py-3 text-sm shadow-lg
      ${dark ? "bg-gray-900 border-gray-700 text-gray-100" : "bg-white border-gray-200 text-gray-800"}`}>
      <p className="font-semibold mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }} className="mt-0.5">
          {p.name}: <span className="font-medium">{Number(p.value).toLocaleString()}</span>
        </p>
      ))}
    </div>
  );
};

const StatCard = ({ label, value, sub, dark }) => (
  <div className={`rounded-xl border p-5 ${dark ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200 shadow-sm"}`}>
    <p className={`text-xs font-semibold uppercase tracking-widest ${dark ? "text-gray-500" : "text-gray-400"}`}>{label}</p>
    <p className={`mt-2 text-3xl font-bold tracking-tight ${dark ? "text-white" : "text-gray-900"}`}>
      {typeof value === "number" ? value.toLocaleString() : value}
    </p>
    {sub && <p className="mt-1 text-xs font-medium text-indigo-500">{sub}</p>}
  </div>
);

const ChartCard = ({ title, children, dark, sub }) => (
  <div className={`rounded-xl border p-6 ${dark ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200 shadow-sm"}`}>
    <p className={`text-sm font-semibold mb-1 ${dark ? "text-gray-300" : "text-gray-700"}`}>{title}</p>
    {sub && <p className={`text-xs mb-4 ${dark ? "text-gray-500" : "text-gray-400"}`}>{sub}</p>}
    {!sub && <div className="mb-5" />}
    {children}
  </div>
);

// ── main component ────────────────────────────────────────────────────────────

export default function ScrapperAnalytics() {
  const [stats, setStats]           = useState([]);
  const [trend, setTrend]           = useState([]);
  const [comparison, setComparison] = useState([]);
  const [growth, setGrowth]         = useState([]);
  const [loading, setLoading]       = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [dark, setDark]             = useState(false);

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [s, t, c, g] = await Promise.all([
        getScrapperAnalytics(),
        getTrend(),
        getComparison(),
        getGrowth(),
      ]);
      setStats(s.data);
      setTrend(t.data);
      setComparison(c.data);
      setGrowth(g.data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await refreshAnalytics();
      await fetchAll();
    } catch (err) {
      console.error(err);
    } finally {
      setRefreshing(false);
    }
  };

  // ── derived data ────────────────────────────────────────────────────────────

  const totalArticles = stats.reduce((s, d) => s + d.articles, 0);
  const totalImages   = stats.reduce((s, d) => s + d.images, 0);
  const avgImages     = totalArticles ? (totalImages / totalArticles).toFixed(1) : 0;
  const topSource     = stats.reduce((top, d) => (d.articles > (top?.articles ?? 0) ? d : top), null);
  const pieData       = stats.map((d) => ({ name: d.source, value: d.articles }));

  const sources = [...new Set(comparison.map((r) => r.source))];
  const compPivot = Object.values(
    comparison.reduce((acc, row) => {
      if (!acc[row.date]) acc[row.date] = { date: row.date };
      acc[row.date][row.source] = row.articles;
      return acc;
    }, {})
  );

  // ── theme tokens ────────────────────────────────────────────────────────────

  const page    = dark ? "bg-gray-950 text-gray-100" : "bg-gray-50 text-gray-900";
  const muted   = dark ? "text-gray-400" : "text-gray-500";
  const heading = dark ? "text-white" : "text-gray-900";
  const divider = dark ? "border-gray-800" : "border-gray-100";
  const gridStroke = dark ? "#1f2937" : "#f1f5f9";
  const axisColor  = dark ? "#6b7280" : "#9ca3af";
  const btnCls  = `text-sm px-3 py-2 rounded-lg border cursor-pointer transition-colors
    ${dark ? "bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700"
           : "bg-white border-gray-200 text-gray-600 hover:bg-gray-50"}`;
  const cardCls = dark ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200 shadow-sm";

  // ── loading ─────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className={`min-h-screen flex flex-col items-center justify-center ${page}`}>
        <div className={`w-9 h-9 rounded-full border-2 border-t-indigo-500
          ${dark ? "border-gray-800" : "border-gray-200"}`}
          style={{ animation: "spin 0.8s linear infinite" }} />
        <p className={`mt-3 text-sm ${muted}`}>Loading analytics...</p>
      </div>
    );
  }

  // ── render ──────────────────────────────────────────────────────────────────

  return (
    <div className={`min-h-screen transition-colors duration-300 ${page}`}>
      <div className="max-w-6xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className={`text-2xl font-bold tracking-tight ${heading}`}>Scraper Analytics</h1>
            {lastUpdated && <p className={`mt-1 text-sm ${muted}`}>Updated at {lastUpdated}</p>}
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setDark(!dark)} className={btnCls}>
              {dark ? "☀ Light" : "☾ Dark"}
            </button>
            <button onClick={handleRefresh} disabled={refreshing} className={btnCls}>
              {refreshing ? "Refreshing..." : "↻ Refresh"}
            </button>
          </div>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard label="Total Articles"       value={totalArticles} dark={dark} />
          <StatCard label="Total Images"         value={totalImages}   dark={dark} />
          <StatCard label="Avg Images / Article" value={Number(avgImages)} dark={dark} />
          <StatCard label="Top Source" value={topSource?.articles ?? 0} sub={topSource?.source} dark={dark} />
        </div>

        {/* Row 1 — current snapshot */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">

          {/* Bar: articles & images per source */}
          <ChartCard title="Articles & Images by Source" dark={dark}>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={stats} margin={{ top: 4, right: 8, left: -10, bottom: 36 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
                <XAxis dataKey="source" tick={{ fill: axisColor, fontSize: 11 }} angle={-30} textAnchor="end" interval={0} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: axisColor, fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip dark={dark} />} cursor={{ fill: dark ? "#ffffff06" : "#00000004" }} />
                <Legend wrapperStyle={{ color: axisColor, fontSize: 12, paddingTop: 12 }} />
                <Bar dataKey="articles" name="Articles" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={32} />
                <Bar dataKey="images"   name="Images"   fill="#0ea5e9" radius={[4, 4, 0, 0]} maxBarSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Pie: article distribution */}
          <ChartCard title="Article Distribution" dark={dark}>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={pieData} cx="50%" cy="50%"
                  innerRadius={65} outerRadius={100}
                  paddingAngle={3} dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={{ stroke: dark ? "#4b5563" : "#d1d5db" }}
                >
                  {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip
                  formatter={(val) => [val.toLocaleString(), "Articles"]}
                  contentStyle={{
                    background: dark ? "#111827" : "#fff",
                    border: `1px solid ${dark ? "#374151" : "#e5e7eb"}`,
                    borderRadius: 8, fontSize: 13,
                    color: dark ? "#f3f4f6" : "#111827",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Row 2 — history charts (only if history data exists) */}
        {trend.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">

            {/* Line: total articles over time */}
            <ChartCard title="Total Articles Over Time" sub="Daily snapshots" dark={dark}>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={trend} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
                  <XAxis dataKey="date" tick={{ fill: axisColor, fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: axisColor, fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip dark={dark} />} cursor={{ stroke: dark ? "#374151" : "#e5e7eb" }} />
                  <Line type="monotone" dataKey="articles" name="Articles" stroke="#6366f1" strokeWidth={2} dot={{ r: 3, fill: "#6366f1" }} activeDot={{ r: 5 }} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Line or Bar: per-source comparison */}
            <ChartCard title="Source Comparison Over Time" sub="Articles per source per day" dark={dark}>
              {/* Custom legend */}
              <div className="flex flex-wrap gap-x-4 gap-y-1.5 mb-4">
                {sources.map((src, i) => (
                  <div key={src} className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: COLORS[i % COLORS.length] }} />
                    <span className={`text-xs ${dark ? "text-gray-400" : "text-gray-500"}`}>{src}</span>
                  </div>
                ))}
              </div>

              {compPivot.length > 1 ? (
                /* Multi-date: line chart */
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={compPivot} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
                    <XAxis dataKey="date" tick={{ fill: axisColor, fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: axisColor, fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip
                      content={({ active, payload, label }) => {
                        if (!active || !payload?.length) return null;
                        return (
                          <div className={`rounded-lg border px-3 py-2.5 shadow-md min-w-[160px]
                            ${dark ? "bg-gray-900 border-gray-700" : "bg-white border-gray-200"}`}>
                            <p className={`text-xs font-medium mb-2 ${dark ? "text-gray-400" : "text-gray-400"}`}>{label}</p>
                            <div className="flex flex-col gap-1">
                              {payload.map((p) => (
                                <div key={p.name} className="flex items-center justify-between gap-4">
                                  <div className="flex items-center gap-1.5">
                                    <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: p.color }} />
                                    <span className={`text-xs ${dark ? "text-gray-300" : "text-gray-600"}`}>{p.name}</span>
                                  </div>
                                  <span className={`text-xs font-semibold tabular-nums ${dark ? "text-white" : "text-gray-900"}`}>
                                    {Number(p.value).toLocaleString()}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      }}
                      cursor={{ stroke: dark ? "#374151" : "#e5e7eb", strokeWidth: 1 }}
                    />
                    {sources.map((src, i) => (
                      <Line key={src} type="monotone" dataKey={src}
                        stroke={COLORS[i % COLORS.length]} strokeWidth={2}
                        dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                /* Single date: horizontal bar fallback */
                <>
                  <p className={`text-xs mb-3 ${dark ? "text-gray-500" : "text-gray-400"}`}>
                    Only one snapshot — refresh more times to see trends
                  </p>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart
                      layout="vertical"
                      data={[...stats].sort((a, b) => b.articles - a.articles)}
                      margin={{ top: 0, right: 16, left: 8, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} horizontal={false} />
                      <XAxis type="number" tick={{ fill: axisColor, fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis type="category" dataKey="source" tick={{ fill: axisColor, fontSize: 11 }} axisLine={false} tickLine={false} width={120} />
                      <Tooltip content={<CustomTooltip dark={dark} />} cursor={{ fill: dark ? "#ffffff06" : "#00000004" }} />
                      <Bar dataKey="articles" name="Articles" radius={[0, 4, 4, 0]} maxBarSize={16}>
                        {stats.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </>
              )}
            </ChartCard>
          </div>
        )}

        {/* Row 3 — growth bar (only if history data exists) */}
        {growth.length > 0 && (
          <div className="mb-5">
            <ChartCard title="Article Growth by Source" sub="Change from previous snapshot" dark={dark}>
              {growth.every(d => d.growth === 0) ? (
                <div className={`flex items-center justify-center h-32 text-sm ${muted}`}>
                  Not enough snapshots yet — refresh a few more times to see growth
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={Math.max(240, growth.length * 36)}>
                  <BarChart
                    layout="vertical"
                    data={[...growth].sort((a, b) => b.growth - a.growth)}
                    margin={{ top: 0, right: 24, left: 8, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} horizontal={false} />
                    <XAxis type="number" tick={{ fill: axisColor, fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis type="category" dataKey="source" tick={{ fill: axisColor, fontSize: 11 }} axisLine={false} tickLine={false} width={130} />
                    <Tooltip content={<CustomTooltip dark={dark} />} cursor={{ fill: dark ? "#ffffff06" : "#00000004" }} />
                    <Bar dataKey="growth" name="Growth" radius={[0, 4, 4, 0]} maxBarSize={18}>
                      {[...growth].sort((a, b) => b.growth - a.growth).map((entry, i) => (
                        <Cell key={i} fill={entry.growth >= 0 ? "#10b981" : "#f43f5e"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </ChartCard>
          </div>
        )}

        {/* Table */}
        <div className={`rounded-xl border overflow-hidden ${cardCls}`}>
          <div className={`px-6 py-4 border-b ${divider}`}>
            <p className={`text-sm font-semibold ${dark ? "text-gray-300" : "text-gray-700"}`}>Source Breakdown</p>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className={`border-b ${divider}`}>
                {["Source", "Articles", "Images", "Img / Article"].map((h) => (
                  <th key={h} className={`px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider ${muted}`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {stats.map((row, i) => (
                <tr key={i} className={`border-b last:border-0 transition-colors ${divider}
                  ${dark ? "hover:bg-gray-800/50" : "hover:bg-gray-50"}`}>
                  <td className={`px-6 py-4 font-medium ${heading}`}>
                    <div className="flex items-center gap-2.5">
                      <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: COLORS[i % COLORS.length] }} />
                      {row.source}
                    </div>
                  </td>
                  <td className={`px-6 py-4 tabular-nums ${muted}`}>{row.articles.toLocaleString()}</td>
                  <td className={`px-6 py-4 tabular-nums ${muted}`}>{row.images.toLocaleString()}</td>
                  <td className={`px-6 py-4 tabular-nums ${muted}`}>
                    {row.articles ? (row.images / row.articles).toFixed(1) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
}
