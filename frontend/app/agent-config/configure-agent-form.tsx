"use client"

import React from "react"
import {
  AgentConfig,
  EnrichmentStatus,
  saveAgentConfig,
  updateAgentConfig,
  retryFailedPosts,
  runEnrichmentNow,
  getEnrichmentStatus,
} from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

const GEMINI_MODELS = [
  { value: "", label: "Default (from server config)" },
  { value: "gemini-2.0-flash", label: "gemini-2.0-flash — fastest, cheapest" },
  { value: "gemini-1.5-flash", label: "gemini-1.5-flash — fast" },
  { value: "gemini-1.5-pro", label: "gemini-1.5-pro — best quality" },
  { value: "gemini-2.0-flash-thinking-exp", label: "gemini-2.0-flash-thinking — reasoning" },
]

const defaultFormValues: Omit<AgentConfig, "id" | "created_at" | "updated_at"> = {
  context_name: "",
  custom_instructions: "",
  focus_topics: [],
  tone: "neutral",
  analysis_depth: "standard",
  llm_model_override: "",
  auto_enrich: true,
  active: true,
}

function statusBadgeVariant(key: string): "default" | "secondary" | "outline" | "destructive" {
  if (key === "enriched") return "default"
  if (key === "failed") return "destructive"
  if (key === "enriching") return "secondary"
  return "outline"
}

interface Props {
  initialConfig: AgentConfig | null
  initialStatus: EnrichmentStatus
}

export function ConfigureAgentForm({ initialConfig, initialStatus }: Props) {
  const [form, setForm] = React.useState<typeof defaultFormValues>(() => {
    if (initialConfig) {
      return {
        context_name: initialConfig.context_name ?? "",
        custom_instructions: initialConfig.custom_instructions ?? "",
        focus_topics: initialConfig.focus_topics ?? [],
        tone: initialConfig.tone ?? "neutral",
        analysis_depth: initialConfig.analysis_depth ?? "standard",
        llm_model_override: initialConfig.llm_model_override ?? "",
        auto_enrich: initialConfig.auto_enrich ?? true,
        active: initialConfig.active ?? true,
      }
    }
    return defaultFormValues
  })

  const [topicsInput, setTopicsInput] = React.useState(
    (initialConfig?.focus_topics ?? []).join(", ")
  )
  const [status, setStatus] = React.useState<EnrichmentStatus>(initialStatus)
  const [saving, setSaving] = React.useState(false)
  const [runState, setRunState] = React.useState<"idle" | "starting" | "running" | "done" | "error">("idle")
  const [retrying, setRetrying] = React.useState(false)
  const [saveMsg, setSaveMsg] = React.useState("")
  const [showPreview, setShowPreview] = React.useState(false)
  const pollRef = React.useRef<ReturnType<typeof setInterval> | null>(null)

  React.useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [])

  function updateField<K extends keyof typeof defaultFormValues>(
    key: K,
    value: (typeof defaultFormValues)[K]
  ) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  function parseTopics(raw: string): string[] {
    return raw
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean)
  }

  async function refreshStatus() {
    try {
      const s = await getEnrichmentStatus()
      setStatus(s)
    } catch {
      // silently ignore
    }
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setSaveMsg("")
    try {
      const payload = {
        ...form,
        focus_topics: parseTopics(topicsInput),
        llm_model_override: form.llm_model_override || null,
        custom_instructions: form.custom_instructions || null,
      }
      if (initialConfig?.id) {
        await updateAgentConfig(initialConfig.id, payload)
      } else {
        await saveAgentConfig(payload)
      }
      setSaveMsg("Configuration saved successfully.")
    } catch {
      setSaveMsg("Failed to save. Please try again.")
    } finally {
      setSaving(false)
    }
  }

  async function handleRunNow() {
    if (pollRef.current) clearInterval(pollRef.current)
    setRunState("starting")
    try {
      await runEnrichmentNow()
      setRunState("running")
      await refreshStatus()

      // Poll every 3 s until no posts are in "enriching" state
      pollRef.current = setInterval(async () => {
        const s = await getEnrichmentStatus()
        setStatus(s)
        if ((s.enriching ?? 0) === 0) {
          clearInterval(pollRef.current!)
          pollRef.current = null
          setRunState("done")
          // Reset "done" badge after 5 s
          setTimeout(() => setRunState("idle"), 5000)
        }
      }, 3000)
    } catch {
      setRunState("error")
      setTimeout(() => setRunState("idle"), 4000)
    }
  }

  async function handleRetryFailed() {
    setRetrying(true)
    try {
      await retryFailedPosts()
      await refreshStatus()
    } catch {
      // ignore
    } finally {
      setRetrying(false)
    }
  }

  const previewPrompt = React.useMemo(() => {
    const topics = parseTopics(topicsInput)
    const sys = [
      "You are a world-class news analyst. Given a raw article, extract and generate structured analysis following a strict JSON schema. Your analysis must be factual, accurate, and written for a general but informed audience. Respond ONLY with valid JSON — no preamble, no markdown fences.",
      form.custom_instructions?.trim() ?? "",
    ]
      .filter(Boolean)
      .join("\n\n")

    const depthMap: Record<string, string> = {
      brief: "Keep all narrative sections very concise: 1-2 sentences each, 2-3 key_highlights bullets maximum.",
      standard: "Use standard depth: 2-4 sentences per narrative section, 3-5 key_highlights bullets.",
      deep: "Provide thorough analysis: 4-6 sentences per narrative section, 5-8 key_highlights bullets.",
    }

    const user = [
      topics.length ? `Focus topics (emphasise these): ${topics.join(", ")}` : "",
      `Tone: ${form.tone}`,
      depthMap[form.analysis_depth] ?? depthMap.standard,
      "\nArticle title: [title of the article]",
      "Article content:\n[article text up to 12,000 characters]",
    ]
      .filter(Boolean)
      .join("\n")

    return { sys, user }
  }, [form, topicsInput])

  return (
    <div className="space-y-6">
      {/* ── Status widget ── */}
      <Card>
        <CardHeader className="border-b pb-3">
          <CardTitle className="text-sm font-semibold">Enrichment Status</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3 pt-4">
          {(["pending", "enriching", "enriched", "failed"] as const).map((key) => (
            <div key={key} className="flex items-center gap-1.5">
              <Badge variant={statusBadgeVariant(key)} className="capitalize">
                {key}
              </Badge>
              <span className="text-sm font-semibold tabular-nums">{status[key] ?? 0}</span>
            </div>
          ))}
          <div className="ml-auto flex items-center gap-2">
            {runState === "running" && (
              <span className="text-xs text-muted-foreground animate-pulse">
                Enriching {status.enriching ?? 0} post{status.enriching !== 1 ? "s" : ""}…
              </span>
            )}
            {runState === "done" && (
              <span className="text-xs text-green-600 font-medium">Done</span>
            )}
            {runState === "error" && (
              <span className="text-xs text-destructive font-medium">Failed to start</span>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={handleRunNow}
              disabled={runState === "starting" || runState === "running"}
            >
              {runState === "starting"
                ? "Starting…"
                : runState === "running"
                ? "Running…"
                : "Run Now"}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRetryFailed}
              disabled={retrying || (status.failed ?? 0) === 0}
            >
              {retrying ? "Resetting…" : `Retry Failed (${status.failed ?? 0})`}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* ── Config form ── */}
      <form onSubmit={handleSave} className="space-y-5">
        <div className="grid gap-2">
          <Label htmlFor="context-name">Context Name</Label>
          <Input
            id="context-name"
            placeholder="e.g. Geopolitics Analyst"
            value={form.context_name}
            onChange={(e) => updateField("context_name", e.target.value)}
            required
          />
        </div>

        <div className="grid gap-2">
          <Label htmlFor="custom-instructions">Custom Instructions</Label>
          <Textarea
            id="custom-instructions"
            placeholder="Additional guidance for the AI — injected into the system prompt verbatim."
            className="min-h-28"
            value={form.custom_instructions ?? ""}
            onChange={(e) => updateField("custom_instructions", e.target.value)}
          />
          <p className="text-xs text-muted-foreground">Max 1,000 characters.</p>
        </div>

        <div className="grid gap-2">
          <Label htmlFor="focus-topics">Focus Topics</Label>
          <Input
            id="focus-topics"
            placeholder="sanctions, trade policy, diplomacy"
            value={topicsInput}
            onChange={(e) => setTopicsInput(e.target.value)}
          />
          <p className="text-xs text-muted-foreground">
            Comma-separated. The AI will pay special attention to these topics.
          </p>
        </div>

        <div className="grid gap-2">
          <Label>Tone</Label>
          <div className="flex gap-4">
            {(["neutral", "analytical", "simplified"] as const).map((t) => (
              <label key={t} className="flex cursor-pointer items-center gap-1.5 text-sm capitalize">
                <input
                  type="radio"
                  name="tone"
                  value={t}
                  checked={form.tone === t}
                  onChange={() => updateField("tone", t)}
                  className="accent-primary"
                />
                {t}
              </label>
            ))}
          </div>
        </div>

        <div className="grid gap-2">
          <Label>Analysis Depth</Label>
          <div className="flex gap-4">
            {(["brief", "standard", "deep"] as const).map((d) => (
              <label key={d} className="flex cursor-pointer items-center gap-1.5 text-sm capitalize">
                <input
                  type="radio"
                  name="analysis_depth"
                  value={d}
                  checked={form.analysis_depth === d}
                  onChange={() => updateField("analysis_depth", d)}
                  className="accent-primary"
                />
                {d}
              </label>
            ))}
          </div>
        </div>

        <div className="grid gap-2">
          <Label htmlFor="llm-model">LLM Model Override</Label>
          <select
            id="llm-model"
            className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            value={form.llm_model_override ?? ""}
            onChange={(e) => updateField("llm_model_override", e.target.value)}
          >
            {GEMINI_MODELS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-3">
          <input
            id="auto-enrich"
            type="checkbox"
            className="accent-primary size-4 cursor-pointer"
            checked={form.auto_enrich}
            onChange={(e) => updateField("auto_enrich", e.target.checked)}
          />
          <Label htmlFor="auto-enrich" className="cursor-pointer">
            Automatically enrich new posts
          </Label>
        </div>

        {saveMsg && (
          <p
            className={`rounded-lg px-3 py-2 text-xs ${
              saveMsg.includes("success")
                ? "bg-muted text-muted-foreground"
                : "bg-destructive/10 text-destructive"
            }`}
          >
            {saveMsg}
          </p>
        )}

        <div className="flex gap-2">
          <Button type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save Configuration"}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => setShowPreview((v) => !v)}
          >
            {showPreview ? "Hide Preview" : "Preview Prompt"}
          </Button>
        </div>
      </form>

      {/* ── Prompt preview ── */}
      {showPreview && (
        <>
          <Separator />
          <div className="space-y-3">
            <h2 className="font-heading text-sm font-semibold text-foreground">
              Assembled Prompt Preview
            </h2>
            <div className="space-y-2">
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                System
              </p>
              <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-muted px-4 py-3 text-xs text-muted-foreground">
                {previewPrompt.sys}
              </pre>
            </div>
            <div className="space-y-2">
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                User
              </p>
              <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-muted px-4 py-3 text-xs text-muted-foreground">
                {previewPrompt.user}
              </pre>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
