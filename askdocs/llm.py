"""LLMProvider interface and the v1 OpenAI-compatible implementation (FR-020).

v1 targets a single local OpenAI-compatible endpoint (configure LLM_BASE_URL and
LLM_MODEL). Cloud providers are future LLMProvider impls (FR-102).
"""

import os
import re
from abc import ABC, abstractmethod

import httpx

DEFAULT_BASE_URL = "http://host.docker.internal:1234/v1"
DEFAULT_MODEL = "google/gemma-4-e4b"

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def strip_think(text: str) -> str:
    """Remove reasoning `<think>...</think>` blocks some local models emit."""
    return _THINK_RE.sub("", text).strip()


class LLMError(RuntimeError):
    """Raised when the LLM endpoint is unreachable or returns an error."""


class LLMProvider(ABC):
    """Interface: "generate an answer from a system + user prompt"."""

    @abstractmethod
    def complete(self, system: str, user: str) -> str: ...


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self._base_url = (base_url or os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self._model = model or os.environ.get("LLM_MODEL", DEFAULT_MODEL)

    def complete(self, system: str, user: str) -> str:
        try:
            response = httpx.post(
                f"{self._base_url}/chat/completions",
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": 0,
                },
                timeout=120,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise LLMError(f"LLM request failed: {e}") from e
        content = response.json()["choices"][0]["message"]["content"]
        return strip_think(content)
