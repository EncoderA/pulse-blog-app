"use client";

import { useState, useCallback } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChevronRight,
  ChevronDown,
  Copy,
  Check,
  RotateCcw,
  Braces,
  AlertCircle,
  Wand2,
  ExternalLink,
  Image as ImageIcon,
} from "lucide-react";

// ── types ──────────────────────────────────────────────────────────────────

type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

// ── helpers ────────────────────────────────────────────────────────────────

const SAMPLE_JSON = `{
  "id": "e5e449e41768ba0abb742c7cee266ad6",
  "source": "BBC World",
  "title": "Jimmy Kimmel rejects White House criticism over Melania widow joke",
  "url": "https://www.bbc.com/news/articles/c04x40d4424o",
  "scraped_at": "2026-04-28T07:29:49.097311",
  "content": "Jimmy Kimmel rejects White House criticism over Melania widow joke\\nLate-night host Jimmy Kimmel has defended a joke in which he called Melania Trump an \\"expectant widow\\" just days before a shooting incident at the White House Correspondents' Dinner.",
  "authors": [],
  "published": "None",
  "images": [
    "https://ichef.bbci.co.uk/news/1024/branded_news/686c/live/8dbc7e00-42cf-11f1-9cf2-2b2a184d3db3.jpg",
    "https://ichef.bbci.co.uk/news/480/cpsprodpb/1399/live/708eb230-42c0-11f1-bd52-e755d604ece4.jpg.webp",
    "https://ichef.bbci.co.uk/news/480/cpsprodpb/e471/live/a27b91b0-42bf-11f1-bd52-e755d604ece4.jpg.webp"
  ],
  "videos": []
}`;

function isUrl(value: string) {
  try {
    const u = new URL(value);
    return u.protocol === "http:" || u.protocol === "https:";
  } catch {
    return false;
  }
}

function isImageUrl(value: string) {
  return isUrl(value) && /\.(jpe?g|png|gif|webp|avif|svg)(\?.*)?$/i.test(value);
}

function typeLabel(value: JsonValue): string {
  if (value === null) return "null";
  if (Array.isArray(value)) return `array[${value.length}]`;
  return typeof value;
}

function typeColor(value: JsonValue): string {
  if (value === null) return "text-rose-400";
  if (typeof value === "boolean") return "text-purple-400";
  if (typeof value === "number") return "text-amber-400";
  if (typeof value === "string") return "text-emerald-400";
  if (Array.isArray(value)) return "text-sky-400";
  return "text-violet-400";
}

function typeBadgeClass(value: JsonValue): string {
  if (value === null) return "bg-rose-500/15 text-rose-400 border-rose-500/30";
  if (typeof value === "boolean") return "bg-purple-500/15 text-purple-400 border-purple-500/30";
  if (typeof value === "number") return "bg-amber-500/15 text-amber-400 border-amber-500/30";
  if (typeof value === "string") return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
  if (Array.isArray(value)) return "bg-sky-500/15 text-sky-400 border-sky-500/30";
  return "bg-violet-500/15 text-violet-400 border-violet-500/30";
}

// ── JsonNode ───────────────────────────────────────────────────────────────

interface JsonNodeProps {
  keyName?: string;
  value: JsonValue;
  depth?: number;
  defaultExpanded?: boolean;
}

function JsonNode({ keyName, value, depth = 0, defaultExpanded = true }: JsonNodeProps) {
  const isComplex = typeof value === "object" && value !== null;
  const [expanded, setExpanded] = useState(defaultExpanded && depth < 3);
  const [imgError, setImgError] = useState(false);

  const indent = depth * 20;

  // ── leaf: render primitive inline ───────────────────────────────────
  if (!isComplex) {
    const strVal = String(value);
    const showUrl = typeof value === "string" && isUrl(value);
    const showImg = typeof value === "string" && isImageUrl(value) && !imgError;

    return (
      <div
        className="group flex flex-col gap-1 rounded-md px-2 py-1 transition-colors hover:bg-white/5"
        style={{ paddingLeft: `${indent + 8}px` }}
      >
        <div className="flex flex-wrap items-center gap-2">
          {keyName !== undefined && (
            <span className="font-mono text-sm font-semibold text-blue-300">
              {keyName}
            </span>
          )}
          {keyName !== undefined && (
            <span className="text-muted-foreground text-xs">:</span>
          )}
          <span
            className={`font-mono text-sm break-all ${typeColor(value)}`}
          >
            {typeof value === "string" ? `"${strVal}"` : strVal}
          </span>
          <span
            className={`inline-flex items-center rounded border px-1.5 py-0.5 font-mono text-[10px] ${typeBadgeClass(value)}`}
          >
            {typeLabel(value)}
          </span>
          {showUrl && (
            <a
              href={strVal}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-sky-400 opacity-0 transition-opacity group-hover:opacity-100 hover:underline"
            >
              <ExternalLink className="size-3" />
              open
            </a>
          )}
        </div>
        {showImg && (
          <div className="mt-1 ml-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={strVal}
              alt={keyName ?? "image"}
              onError={() => setImgError(true)}
              className="max-h-48 max-w-xs rounded-md border border-white/10 object-cover shadow-lg transition-transform hover:scale-105"
            />
          </div>
        )}
      </div>
    );
  }

  // ── complex: object / array ─────────────────────────────────────────
  const isArray = Array.isArray(value);
  const entries = isArray
    ? (value as JsonValue[]).map((v, i) => [String(i), v] as [string, JsonValue])
    : Object.entries(value as { [k: string]: JsonValue });

  const openBracket = isArray ? "[" : "{";
  const closeBracket = isArray ? "]" : "}";
  const count = entries.length;

  return (
    <div style={{ paddingLeft: `${indent}px` }}>
      {/* header row */}
      <button
        onClick={() => setExpanded((p) => !p)}
        className="group flex w-full items-center gap-1.5 rounded-md px-2 py-1 text-left transition-colors hover:bg-white/5"
      >
        <span className="text-muted-foreground transition-transform duration-200">
          {expanded ? (
            <ChevronDown className="size-3.5" />
          ) : (
            <ChevronRight className="size-3.5" />
          )}
        </span>

        {keyName !== undefined && (
          <span className="font-mono text-sm font-semibold text-blue-300">
            {keyName}
          </span>
        )}
        {keyName !== undefined && (
          <span className="text-muted-foreground text-xs">:</span>
        )}

        <span className={`font-mono text-sm font-semibold ${typeColor(value)}`}>
          {openBracket}
        </span>

        {!expanded && (
          <span className="text-muted-foreground font-mono text-xs">
            {count} {isArray ? (count === 1 ? "item" : "items") : count === 1 ? "key" : "keys"}
          </span>
        )}

        <span
          className={`inline-flex items-center rounded border px-1.5 py-0.5 font-mono text-[10px] ${typeBadgeClass(value)}`}
        >
          {typeLabel(value)}
        </span>
      </button>

      {/* children */}
      {expanded && (
        <div className="border-l border-white/10 ml-3">
          {entries.map(([k, v]) => (
            <JsonNode
              key={k}
              keyName={isArray ? undefined : k}
              value={v}
              depth={depth + 1}
              defaultExpanded={defaultExpanded}
            />
          ))}
        </div>
      )}

      {/* close bracket */}
      {expanded && (
        <div
          className="font-mono text-sm px-2"
          style={{ paddingLeft: `${indent + 8}px` }}
        >
          <span className={typeColor(value)}>{closeBracket}</span>
        </div>
      )}
    </div>
  );
}

// ── main page ──────────────────────────────────────────────────────────────

export default function JsonVisualizerPage() {
  const [inputText, setInputText] = useState(SAMPLE_JSON);
  const [parsed, setParsed] = useState<JsonValue | null>(() => {
    try {
      return JSON.parse(SAMPLE_JSON);
    } catch {
      return null;
    }
  });
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [copiedFormatted, setCopiedFormatted] = useState(false);
  const [stats, setStats] = useState<{ keys: number; depth: number } | null>(
    () => computeStats(JSON.parse(SAMPLE_JSON))
  );

  function computeStats(val: JsonValue): { keys: number; depth: number } {
    let keys = 0;
    let maxDepth = 0;
    function traverse(v: JsonValue, d: number) {
      maxDepth = Math.max(maxDepth, d);
      if (typeof v === "object" && v !== null) {
        const entries = Array.isArray(v)
          ? v
          : Object.values(v as { [k: string]: JsonValue });
        for (const child of entries) {
          if (!Array.isArray(v)) keys++;
          traverse(child as JsonValue, d + 1);
        }
      }
    }
    traverse(val, 0);
    return { keys, depth: maxDepth };
  }

  const handleParse = useCallback(() => {
    try {
      const result = JSON.parse(inputText);
      setParsed(result);
      setError(null);
      setStats(computeStats(result));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Invalid JSON");
      setParsed(null);
      setStats(null);
    }
  }, [inputText]);

  const handleReset = () => {
    setInputText(SAMPLE_JSON);
    const sample = JSON.parse(SAMPLE_JSON);
    setParsed(sample);
    setError(null);
    setStats(computeStats(sample));
  };

  const handleCopyInput = async () => {
    await navigator.clipboard.writeText(inputText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCopyFormatted = async () => {
    if (!parsed) return;
    await navigator.clipboard.writeText(JSON.stringify(parsed, null, 2));
    setCopiedFormatted(true);
    setTimeout(() => setCopiedFormatted(false), 2000);
  };

  const handleFormat = () => {
    try {
      const result = JSON.parse(inputText);
      setInputText(JSON.stringify(result, null, 2));
      setParsed(result);
      setError(null);
      setStats(computeStats(result));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Invalid JSON");
    }
  };

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      {/* page header */}
      <div className="flex flex-col gap-4">
        <div>
          <Badge variant="secondary" className="mb-4">
            JSON Visualizer
          </Badge>
          <h1 className="font-heading text-3xl font-semibold tracking-normal sm:text-4xl">
            Visualize JSON objects
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-muted-foreground">
            Paste any JSON and explore it as an interactive tree. Collapse
            nodes, preview images, and open URLs inline.
          </p>
        </div>

        {/* stats row */}
        {parsed && stats && (
          <div className="flex flex-wrap gap-3">
            {[
              { label: "Type", value: Array.isArray(parsed) ? "Array" : typeof parsed === "object" ? "Object" : typeof parsed },
              { label: "Keys", value: stats.keys },
              { label: "Depth", value: stats.depth },
              {
                label: "Size",
                value: `${new Blob([inputText]).size.toLocaleString()} B`,
              },
            ].map((s) => (
              <div
                key={s.label}
                className="flex items-center gap-2 rounded-lg border bg-muted/40 px-3 py-1.5 text-sm"
              >
                <span className="text-muted-foreground">{s.label}</span>
                <span className="font-mono font-semibold">{s.value}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* two-column layout */}
      <div className="grid flex-1 gap-6 lg:grid-cols-2">
        {/* ── left: input ─────────────────────────────────────────────── */}
        <Card className="flex flex-col rounded-xl border bg-card">
          <CardHeader className="flex flex-row items-center justify-between border-b px-4 py-3">
            <CardTitle className="flex items-center gap-2 text-sm font-semibold">
              <Braces className="size-4 text-primary" />
              JSON Input
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="h-7 gap-1 px-2 text-xs"
                onClick={handleCopyInput}
              >
                {copied ? (
                  <Check className="size-3.5 text-emerald-400" />
                ) : (
                  <Copy className="size-3.5" />
                )}
                {copied ? "Copied!" : "Copy"}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 gap-1 px-2 text-xs"
                onClick={handleFormat}
              >
                <Wand2 className="size-3.5" />
                Format
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 gap-1 px-2 text-xs"
                onClick={handleReset}
              >
                <RotateCcw className="size-3.5" />
                Reset
              </Button>
            </div>
          </CardHeader>

          <CardContent className="flex flex-1 flex-col gap-3 p-4">
            <textarea
              id="json-input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              spellCheck={false}
              className="flex-1 min-h-[480px] w-full resize-none rounded-lg border bg-muted/30 p-4 font-mono text-xs leading-relaxed text-foreground outline-none transition-colors focus:border-primary focus:bg-background placeholder:text-muted-foreground"
              placeholder="Paste your JSON here…"
            />

            {error && (
              <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                <AlertCircle className="mt-0.5 size-4 shrink-0" />
                <span className="font-mono text-xs break-all">{error}</span>
              </div>
            )}

            <Button id="visualize-btn" onClick={handleParse} className="w-full gap-2">
              <Braces className="size-4" />
              Visualize
            </Button>
          </CardContent>
        </Card>

        {/* ── right: tree view ─────────────────────────────────────────── */}
        <Card className="flex flex-col rounded-xl border bg-card">
          <CardHeader className="flex flex-row items-center justify-between border-b px-4 py-3">
            <CardTitle className="flex items-center gap-2 text-sm font-semibold">
              <ImageIcon className="size-4 text-primary" />
              Tree View
            </CardTitle>
            {parsed && (
              <Button
                variant="ghost"
                size="sm"
                className="h-7 gap-1 px-2 text-xs"
                onClick={handleCopyFormatted}
              >
                {copiedFormatted ? (
                  <Check className="size-3.5 text-emerald-400" />
                ) : (
                  <Copy className="size-3.5" />
                )}
                {copiedFormatted ? "Copied!" : "Copy formatted"}
              </Button>
            )}
          </CardHeader>

          <CardContent className="flex-1 overflow-auto p-4">
            {parsed !== null ? (
              <div className="font-mono text-sm">
                <JsonNode value={parsed} defaultExpanded={true} />
              </div>
            ) : (
              <div className="flex h-full min-h-[480px] flex-col items-center justify-center gap-4 text-center text-muted-foreground">
                <Braces className="size-12 opacity-20" />
                <div>
                  <p className="text-sm font-medium">No valid JSON yet</p>
                  <p className="mt-1 text-xs">
                    Paste JSON on the left and click <strong>Visualize</strong>.
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
