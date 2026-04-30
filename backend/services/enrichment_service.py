import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select, text

from core.config import settings
from core.database import engine
from models.timeline_post import TimelinePost
from models.timeline_agent_config import TimelineAgentConfig
from services.llm_client import LLMClient, LLMError

logger = logging.getLogger(__name__)

# ── JSON output schema description sent inside the user prompt ──────────────

_JSON_SCHEMA = """
{
  "quick_take": "string — 1-2 sentences, the single most important takeaway",
  "background": "string — 2-4 sentences, historical/contextual setup",
  "what_happened": "string — 2-4 sentences, the specific events in this article",
  "key_highlights": ["string", "..."],
  "impact": "string — 2-3 sentences, why this matters short-term and long-term",
  "whats_next": "string — 2-3 sentences, expected next steps or uncertainties",
  "overview": "string — 1 sentence factual one-liner for the key facts sidebar",
  "impacts_detail": "string — 1-2 sentences, implementation or enforcement detail",
  "is_ai_policy": true_or_false,
  "events": [
    {
      "event_time": "ISO 8601 date string or null",
      "event_title": "string — short headline for this moment",
      "event_content": "string — 1-3 sentences describing this moment",
      "sequence_order": 1
    }
  ],
  "quotes": [
    {
      "quote_text": "string — verbatim or near-verbatim from article",
      "attributed_to": "string — person name and title if available",
      "display_order": 1
    }
  ]
}
"""

_DEPTH_INSTRUCTIONS = {
    "brief": (
        "Keep all narrative sections very concise: "
        "1-2 sentences each, 2-3 key_highlights bullets maximum."
    ),
    "standard": (
        "Use standard depth: "
        "2-4 sentences per narrative section, 3-5 key_highlights bullets."
    ),
    "deep": (
        "Provide thorough analysis: "
        "4-6 sentences per narrative section, 5-8 key_highlights bullets."
    ),
}

_BASE_SYSTEM = (
    "You are a world-class news analyst. "
    "Given a raw article, extract and generate structured analysis "
    "following a strict JSON schema. "
    "Your analysis must be factual, accurate, and written for a general but informed audience. "
    "Respond ONLY with valid JSON — no preamble, no markdown fences."
)


class EnrichmentService:
    def __init__(self, db: Session, llm: LLMClient) -> None:
        self.db = db
        self.llm = llm

    # ── Public entry point ───────────────────────────────────────────────────

    async def enrich_post(
        self, post: TimelinePost, agent_config: Optional[TimelineAgentConfig]
    ) -> bool:
        """
        Enrich a single pending timeline post.
        Returns True on success, False on failure (caller handles retry_count).
        Always rolls back the session on failure so the caller can still write.
        """
        try:
            content = self._get_raw_content(post)
            system_prompt = self._build_system_prompt(agent_config)
            user_message = self._build_user_message(post.title or "", content, agent_config)
            data = await self.llm.complete_json(system_prompt, user_message)
            if not self._validate_output(data):
                raise ValueError("LLM output failed validation checks")
            self._write_results(post, data, agent_config)
            logger.info("Enriched timeline post id=%s title=%r", post.id, post.title)
            return True
        except LLMError as exc:
            logger.warning("LLM error for post id=%s: %s", post.id, exc)
            self.db.rollback()
            return False
        except Exception as exc:
            logger.error("Unexpected error enriching post id=%s: %s", post.id, exc, exc_info=True)
            self.db.rollback()
            return False

    # ── Content loading ──────────────────────────────────────────────────────

    def _get_raw_content(self, post: TimelinePost) -> str:
        """
        Load raw article content from the posts table (title-cased column names).
        Concatenates all text columns for richer context.
        Falls back to existing timeline_event content, then short_summary.
        Each query runs in its own savepoint to prevent a failed SQL from
        aborting the outer transaction.
        """
        try:
            row = self.db.exec(
                text(
                    'SELECT "Background", "News", "Highlights", "Impact", "Whats_Next" '
                    'FROM posts WHERE "Source_Url" = :src LIMIT 1'
                ).bindparams(src=post.source_url or "")
            ).first()
            if row:
                parts = [str(v) for v in row if v]
                combined = " ".join(parts).strip()
                if combined:
                    return combined[:12000]
        except Exception:
            self.db.rollback()

        # Fallback: pull from existing timeline_events rows
        try:
            rows = self.db.exec(
                text(
                    "SELECT event_content FROM timeline_events "
                    "WHERE post_id = :pid ORDER BY sequence_order"
                ).bindparams(pid=post.id)
            ).all()
            combined = " ".join(r[0] for r in rows if r[0]).strip()
            if combined:
                return combined[:12000]
        except Exception:
            self.db.rollback()

        return post.short_summary or post.title or ""

    # ── Prompt assembly ──────────────────────────────────────────────────────

    def _build_system_prompt(self, agent_config: Optional[TimelineAgentConfig]) -> str:
        parts = [_BASE_SYSTEM]
        if agent_config and agent_config.custom_instructions:
            parts.append(agent_config.custom_instructions.strip())
        return "\n\n".join(parts)

    def _build_user_message(
        self,
        title: str,
        content: str,
        agent_config: Optional[TimelineAgentConfig],
    ) -> str:
        lines = []

        if agent_config:
            if agent_config.focus_topics:
                lines.append(
                    f"Focus topics (emphasise these): {', '.join(agent_config.focus_topics)}"
                )
            tone = agent_config.tone or "neutral"
            depth = agent_config.analysis_depth or "standard"
            lines.append(f"Tone: {tone}")
            lines.append(_DEPTH_INSTRUCTIONS.get(depth, _DEPTH_INSTRUCTIONS["standard"]))

        lines.append(f"\nArticle title: {title}")
        lines.append(f"Article content:\n{content}")
        lines.append(f"\nRespond ONLY with a valid JSON object matching this schema:\n{_JSON_SCHEMA}")

        return "\n".join(lines)

    # ── Validation ───────────────────────────────────────────────────────────

    def _validate_output(self, data: dict) -> bool:
        required_strings = ["quick_take", "background", "what_happened", "impact", "whats_next"]
        for key in required_strings:
            val = data.get(key)
            if not val or not isinstance(val, str) or len(val.strip()) < 10:
                logger.warning("Validation failed: field %r missing or too short", key)
                return False

        if not isinstance(data.get("events"), list) or len(data["events"]) == 0:
            logger.warning("Validation failed: events list is empty or missing")
            return False

        if not isinstance(data.get("key_highlights"), list) or len(data["key_highlights"]) == 0:
            logger.warning("Validation failed: key_highlights list is empty or missing")
            return False

        return True

    # ── DB writes ────────────────────────────────────────────────────────────

    def _write_results(
        self,
        post: TimelinePost,
        data: dict,
        agent_config: Optional[TimelineAgentConfig],
    ) -> None:
        now = datetime.now(timezone.utc)
        model_used = (
            agent_config.llm_model_override
            if agent_config and agent_config.llm_model_override
            else self.llm.model_name
        )

        # Update narrative fields on timeline_posts
        post.quick_take = data.get("quick_take")
        post.background = data.get("background")
        post.what_happened = data.get("what_happened")
        post.key_highlights = "\n".join(data.get("key_highlights", []))
        post.impact = data.get("impact")
        post.whats_next = data.get("whats_next")
        post.overview = data.get("overview")
        post.impacts_detail = data.get("impacts_detail")
        post.is_ai_policy = bool(data.get("is_ai_policy", False))
        post.ingest_status = "enriched"
        post.enriched_at = now
        post.enrichment_model = model_used
        post.agent_config_id = agent_config.id if agent_config else None
        post.updated_at = now
        self.db.add(post)

        # Replace placeholder events with LLM-extracted events
        self.db.exec(
            text("DELETE FROM timeline_events WHERE post_id = :pid")
            .bindparams(pid=post.id)
        )

        for idx, event in enumerate(data.get("events", []), start=1):
            self.db.exec(
                text("""
                    INSERT INTO timeline_events
                        (post_id, event_time, event_title, event_content, sequence_order)
                    VALUES (:post_id, :event_time, :event_title, :event_content, :seq)
                """).bindparams(
                    post_id=post.id,
                    event_time=event.get("event_time"),
                    event_title=event.get("event_title", ""),
                    event_content=event.get("event_content", ""),
                    seq=event.get("sequence_order", idx),
                )
            )

        # Insert extracted quotes (only if article had quotes)
        for idx, quote in enumerate(data.get("quotes", []), start=1):
            if not quote.get("quote_text"):
                continue
            self.db.exec(
                text("""
                    INSERT INTO timeline_quotes (post_id, quote_text, attributed_to, display_order)
                    VALUES (:post_id, :quote_text, :attributed_to, :display_order)
                    ON CONFLICT DO NOTHING
                """).bindparams(
                    post_id=post.id,
                    quote_text=quote.get("quote_text", ""),
                    attributed_to=quote.get("attributed_to"),
                    display_order=quote.get("display_order", idx),
                )
            )

        self.db.commit()


# ── Batch scheduler function ─────────────────────────────────────────────────

async def run_enrichment_batch() -> None:
    """
    Called by APScheduler every ENRICHMENT_INTERVAL_MINUTES.
    Picks up pending timeline posts and enriches them with Gemini.
    """
    if not settings.GEMINI_API_KEY:
        logger.debug("Enrichment skipped: GEMINI_API_KEY is not set")
        return

    with Session(engine) as db:
        # Load active agent config (if any)
        agent_config = db.exec(
            select(TimelineAgentConfig)
            .where(TimelineAgentConfig.active == True)
            .order_by(TimelineAgentConfig.id.desc())
            .limit(1)
        ).first()

        if agent_config and not agent_config.auto_enrich:
            logger.info("Enrichment skipped: active AgentConfig has auto_enrich=False")
            return

        # Pick pending posts that haven't exceeded retry limit
        pending = db.exec(
            select(TimelinePost)
            .where(
                TimelinePost.ingest_status.in_(["pending", "failed"]),
                TimelinePost.retry_count < settings.ENRICHMENT_MAX_RETRIES,
            )
            .order_by(TimelinePost.created_at.asc())
            .limit(settings.ENRICHMENT_BATCH_SIZE)
        ).all()

        if not pending:
            logger.debug("Enrichment batch: no pending posts found")
            return

        logger.info("Enrichment batch: processing %d posts", len(pending))

        model_name = (
            agent_config.llm_model_override
            if agent_config and agent_config.llm_model_override
            else settings.LLM_MODEL
        )

        llm = LLMClient(
            provider=settings.LLM_PROVIDER,
            model=model_name,
            api_key=settings.GEMINI_API_KEY,
        )
        service = EnrichmentService(db=db, llm=llm)

        for post in pending:
            # Mark as enriching to avoid double-processing
            post.ingest_status = "enriching"
            db.add(post)
            db.commit()

            success = await service.enrich_post(post, agent_config)

            if not success:
                try:
                    db.rollback()
                except Exception:
                    pass
                post.retry_count = (post.retry_count or 0) + 1
                post.ingest_status = (
                    "failed" if post.retry_count >= settings.ENRICHMENT_MAX_RETRIES else "pending"
                )
                db.add(post)
                db.commit()
                logger.warning(
                    "Enrichment failed for post id=%s retry_count=%s status=%s",
                    post.id,
                    post.retry_count,
                    post.ingest_status,
                )
