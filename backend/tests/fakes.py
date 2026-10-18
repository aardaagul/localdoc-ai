"""Testlerde kullanılan sahte model istemcisi (Ollama gerektirmez)."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Sequence

from app.services.ollama_client import OllamaError

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


class FakeLLMClient:
    """Deterministik, ağ erişimi olmayan bir LLM/embedding istemcisi.

    - ``chat_reply``: ``chat`` çağrılarında döndürülecek sabit metin.
    - ``embed_dim``: üretilen embedding boyutu.
    - ``fail_chat`` / ``fail_embed``: ilgili işlemi hata ile sonuçlandırır.
    """

    def __init__(
        self,
        *,
        available: bool = True,
        chat_reply: str = "Sahte cevap [1].",
        embed_dim: int = 64,
        fail_chat: bool = False,
        fail_embed: bool = False,
    ) -> None:
        self.available = available
        self.chat_reply = chat_reply
        self.embed_dim = embed_dim
        self.fail_chat = fail_chat
        self.fail_embed = fail_embed
        self.chat_calls: list[list[dict]] = []
        self.embed_calls: list[list[str]] = []

    async def is_available(self) -> bool:
        return self.available

    async def list_models(self) -> list[str]:
        return ["fake-chat", "fake-embed"]

    async def chat(self, messages: Sequence[dict], *, temperature: float = 0.1) -> str:
        self.chat_calls.append(list(messages))
        if self.fail_chat:
            raise OllamaError("Yerel model kapalı (test).")
        return self.chat_reply

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        self.embed_calls.append(list(texts))
        if self.fail_embed:
            raise OllamaError("Embedding modeli kapalı (test).")
        return [self._vector(text) for text in texts]

    def _vector(self, text: str) -> list[float]:
        vector = [0.0] * self.embed_dim
        for token in _TOKEN_RE.findall((text or "").lower()):
            digest = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            vector[digest % self.embed_dim] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
