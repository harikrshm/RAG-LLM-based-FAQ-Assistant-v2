"""
LLM Service

Provides an abstraction over different Large Language Model providers
so the application can switch between Gemini and open-source/local
models through configuration.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, Field

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class LLMGenerationResult(BaseModel):
    """
    Represents the result of an LLM generation call.
    """

    provider: str
    model: str
    text: str
    finish_reason: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    raw_response: Optional[Any] = Field(default=None, description="Provider specific payload")


class LLMService:
    """
    Service responsible for interacting with the configured LLM provider.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        self.provider = (provider or settings.LLM_PROVIDER).lower()
        self.model = model or settings.LLM_MODEL
        self.temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        self.request_timeout = settings.LLM_REQUEST_TIMEOUT

        self._client = self._init_client()

        logger.info("Initialized LLMService with provider=%s model=%s", self.provider, self.model)

    def _init_client(self):
        """
        Initialize provider specific client if required.
        """
        if self.provider == "gemini":
            return self._init_gemini_client()
        if self.provider == "local":
            if not settings.LOCAL_LLM_URL:
                logger.warning("LOCAL_LLM_URL is not configured; local provider calls will fail.")
            return None

        if self.provider in {"openai", "anthropic"}:
            logger.warning("Provider '%s' is not yet implemented.", self.provider)
            return None

        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _init_gemini_client(self):
        try:
            import google.generativeai as genai
        except ImportError as exc:  # pragma: no cover - dependency issue
            raise ImportError(
                "google-generativeai is required for Gemini provider. "
                "Please install it via 'pip install google-generativeai'."
            ) from exc

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._gemini_module = genai
        return genai.GenerativeModel(self.model)

    def build_prompt(
        self,
        user_query: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        guardrails: Optional[List[str]] = None,
    ) -> str:
        """
        Construct the final prompt string sent to the LLM.
        """
        sections: List[str] = []

        if system_prompt:
            sections.append(f"System Instructions:\n{system_prompt.strip()}")

        if guardrails:
            guardrail_lines = "\n".join(f"- {rule.strip()}" for rule in guardrails if rule.strip())
            if guardrail_lines:
                sections.append(f"Guardrails:\n{guardrail_lines}")

        if context:
            sections.append(f"Reference Context:\n{context.strip()}")

        sections.append(f"User Question:\n{user_query.strip()}")

        sections.append(
            "Response Guidelines:\n"
            "- Provide factual information only.\n"
            "- Cite provided sources when applicable.\n"
            "- Do not provide investment advice or recommendations.\n"
            "- Be concise and use clear language."
        )

        return "\n\n".join(sections).strip()

    def generate(
        self,
        prompt: str,
        *,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        guardrails: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMGenerationResult:
        """
        Generate a response synchronously using the configured LLM provider.
        """
        final_prompt = self.build_prompt(
            user_query=prompt,
            context=context,
            system_prompt=system_prompt,
            guardrails=guardrails,
        )

        provider_temperature = temperature if temperature is not None else self.temperature
        provider_max_tokens = max_tokens or self.max_tokens

        if self.provider == "gemini":
            return self._generate_with_gemini(
                final_prompt,
                temperature=provider_temperature,
                max_tokens=provider_max_tokens,
                **kwargs,
            )

        if self.provider == "local":
            return self._generate_with_local(
                final_prompt,
                temperature=provider_temperature,
                max_tokens=provider_max_tokens,
                **kwargs,
            )

        raise NotImplementedError(f"Provider '{self.provider}' is not implemented yet.")

    async def agenerate(self, *args, **kwargs) -> LLMGenerationResult:
        """
        Async wrapper around generate() so FastAPI routes can await LLM calls.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self.generate(*args, **kwargs))

    def _generate_with_gemini(
        self,
        prompt: str,
        *,
        temperature: float,
        max_tokens: int,
        **kwargs: Any,
    ) -> LLMGenerationResult:
        if not self._client:
            raise RuntimeError("Gemini client is not initialized.")

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": kwargs.get("top_p", 0.95),
            "top_k": kwargs.get("top_k", 40),
        }

        try:
            response = self._client.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=kwargs.get("safety_settings"),
            )
        except Exception as exc:  # pragma: no cover - network
            logger.exception("Gemini generation failed: %s", exc)
            raise

        text = (response.text or "").strip()

        if not text and response.candidates:
            parts = []
            for part in response.candidates[0].content.parts:
                part_text = getattr(part, "text", None)
                if part_text:
                    parts.append(part_text)
            text = "\n".join(parts).strip()

        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", None)
        completion_tokens = getattr(usage, "candidates_token_count", None)
        total_tokens = getattr(usage, "total_token_count", None)
        finish_reason = None
        if response.candidates:
            finish_reason = getattr(response.candidates[0], "finish_reason", None)

        raw_payload: Any
        if hasattr(response, "to_dict"):
            raw_payload = response.to_dict()
        elif hasattr(response, "_raw_response") and hasattr(response._raw_response, "text"):
            raw_payload = response._raw_response.text
        else:
            raw_payload = str(response)

        return LLMGenerationResult(
            provider="gemini",
            model=self.model,
            text=text,
            finish_reason=finish_reason,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            raw_response=raw_payload,
        )

    def _generate_with_local(
        self,
        prompt: str,
        *,
        temperature: float,
        max_tokens: int,
        **kwargs: Any,
    ) -> LLMGenerationResult:
        if not settings.LOCAL_LLM_URL:
            raise ValueError("LOCAL_LLM_URL must be configured for local LLM provider.")

        headers = kwargs.get("headers", {}).copy()
        if settings.LOCAL_LLM_API_KEY and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {settings.LOCAL_LLM_API_KEY}"

        payload: Dict[str, Any] = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "model": self.model,
        }
        payload.update(kwargs.get("payload_overrides", {}))

        try:
            response = requests.post(
                settings.LOCAL_LLM_URL,
                json=payload,
                headers=headers,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("Local LLM request failed: %s", exc)
            raise

        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error("Local LLM returned non-JSON response: %s", response.text[:200])
            raise

        text = (
            data.get("text")
            or data.get("response")
            or data.get("data")
            or ""
        )

        usage = data.get("usage", {})

        return LLMGenerationResult(
            provider="local",
            model=data.get("model", self.model),
            text=text.strip(),
            finish_reason=data.get("finish_reason"),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            raw_response=data,
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Provide diagnostics for monitoring endpoints.
        """
        status = "healthy"
        details: Dict[str, Any] = {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if self.provider == "gemini":
            details["client_initialized"] = self._client is not None
            if not self._client:
                status = "unhealthy"
        elif self.provider == "local":
            details["endpoint"] = settings.LOCAL_LLM_URL
            if not settings.LOCAL_LLM_URL:
                status = "unhealthy"
                details["error"] = "LOCAL_LLM_URL not configured"

        return {"status": status, "details": details}


# Singleton helper ---------------------------------------------------------
_llm_service_instance: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Return a singleton instance of LLMService.
    """
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance


