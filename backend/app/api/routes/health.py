"""Sağlık/durum uç noktası."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_llm_client
from app.core.config import get_settings
from app.services.ollama_client import LLMClient, OllamaError

router = APIRouter()


@router.get("/health", summary="Uygulama ve model durumu")
async def health(client: LLMClient = Depends(get_llm_client)) -> dict:
    settings = get_settings()
    available = await client.is_available()

    models: list[str] = []
    if available:
        try:
            models = await client.list_models()
        except OllamaError:
            models = []

    return {
        "status": "ok",
        "app": settings.app_name,
        "ollama": {
            "available": available,
            "base_url": settings.ollama_base_url,
            "chat_model": settings.ollama_chat_model,
            "embed_model": settings.ollama_embed_model,
            "models": models,
        },
    }
