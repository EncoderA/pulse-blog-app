import asyncio
import json
import logging

import google.generativeai as genai

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Base error for all LLM failures."""


class LLMParseError(LLMError):
    """Gemini returned content that could not be parsed as JSON."""


class LLMContentError(LLMError):
    """Gemini blocked the request due to safety filters."""


class LLMClient:
    """
    Gemini-backed LLM wrapper with structured JSON output.
    Provider field is retained so future providers can be added via config.
    """

    def __init__(self, provider: str, model: str, api_key: str) -> None:
        if provider != "gemini":
            raise ValueError(f"Unsupported LLM provider: {provider!r}. Only 'gemini' is supported.")

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            model_name=model,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2,
                max_output_tokens=2048,
            ),
        )
        self.model_name = model
        logger.info("LLMClient initialised: provider=gemini model=%s", model)

    async def complete_json(self, system: str, user: str) -> dict:
        """
        Call Gemini with a combined system+user prompt and return a parsed JSON dict.

        Raises:
            LLMContentError  — response blocked by safety filters
            LLMParseError    — response text is not valid JSON
            LLMError         — any other Gemini / network failure
        """
        prompt = f"{system}\n\n{user}"
        try:
            response = await asyncio.to_thread(self._model.generate_content, prompt)
        except Exception as exc:
            raise LLMError(f"Gemini API call failed: {exc}") from exc

        candidate = response.candidates[0] if response.candidates else None

        if candidate is None or str(getattr(candidate, "finish_reason", "")) not in ("1", "STOP"):
            # Safety filter or unexpected stop
            feedback = getattr(response, "prompt_feedback", None)
            raise LLMContentError(
                f"Gemini response blocked or incomplete. "
                f"finish_reason={getattr(candidate, 'finish_reason', 'N/A')} "
                f"prompt_feedback={feedback}"
            )

        raw = response.text.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LLMParseError(
                f"JSON parse failed: {exc}\nFirst 500 chars of response: {raw[:500]}"
            ) from exc
