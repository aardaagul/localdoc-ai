"""Ortak FastAPI bağımlılıkları."""

from __future__ import annotations

from app.services.ollama_client import LLMClient, OllamaClient


def get_llm_client() -> LLMClient:
    """Yerel model istemcisini döndürür (testlerde kolayca değiştirilebilir)."""
    return OllamaClient()
