"""Ollama (yerel model sunucusu) ile iletişim kuran istemci.

Ollama kurulu değilse veya kapalıysa uygulama çökmemeli; bu durumda
``OllamaError`` fırlatılır ve üst katmanlar (API) anlaşılır bir hata döndürür.
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

import httpx

from app.core.config import get_settings


class OllamaError(RuntimeError):
    """Ollama servisine erişilemediğinde veya model hata döndürdüğünde fırlatılır."""


@runtime_checkable
class LLMClient(Protocol):
    """Sohbet ve embedding üretebilen bir model istemcisi arayüzü."""

    async def is_available(self) -> bool: ...

    async def list_models(self) -> list[str]: ...

    async def chat(self, messages: Sequence[dict], *, temperature: float = ...) -> str: ...

    async def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class OllamaClient:
    """HTTP üzerinden Ollama REST API'sini kullanan istemci."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        chat_model: str | None = None,
        embed_model: str | None = None,
        timeout: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.chat_model = chat_model or settings.ollama_chat_model
        self.embed_model = embed_model or settings.ollama_embed_model
        self.timeout = timeout or settings.ollama_timeout
        self._transport = transport

    # ---- yardımcılar ----
    def _client(self, timeout: float | None = None) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=timeout or self.timeout,
            transport=self._transport,
        )

    # ---- genel API ----
    async def is_available(self) -> bool:
        try:
            async with self._client(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def list_models(self) -> list[str]:
        try:
            async with self._client(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise OllamaError(f"Ollama'ya erişilemedi: {exc}") from exc
        return [model.get("name", "") for model in data.get("models", [])]

    async def chat(self, messages: Sequence[dict], *, temperature: float = 0.1) -> str:
        payload = {
            "model": self.chat_model,
            "messages": list(messages),
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            async with self._client() as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise OllamaError(
                f"Yerel model ('{self.chat_model}') {self.timeout:.0f} saniyede yanıt vermedi. "
                "İlk soruda model belleğe yükleniyor olabilir: birkaç saniye sonra tekrar "
                "deneyin. Sorun sürerse OLLAMA_TIMEOUT değerini artırın veya daha küçük bir "
                f"model seçin. Ayrıntı: {exc}"
            ) from exc
        except httpx.HTTPError as exc:
            raise OllamaError(
                f"Yerel sohbet modeli yanıt vermedi ('{self.chat_model}'). "
                f"Ollama çalışıyor mu ve model indirildi mi? Ayrıntı: {exc}"
            ) from exc

        content = (data.get("message") or {}).get("content", "")
        if not content.strip():
            raise OllamaError("Model boş bir yanıt döndürdü.")
        return content.strip()

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        payload = {"model": self.embed_model, "input": list(texts)}
        try:
            async with self._client() as client:
                response = await client.post(f"{self.base_url}/api/embed", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise OllamaError(
                f"Embedding modeli ('{self.embed_model}') zaman aşımına uğradı. "
                f"Ayrıntı: {exc}"
            ) from exc
        except httpx.HTTPError as exc:
            raise OllamaError(
                f"Embedding modeli çalıştırılamadı ('{self.embed_model}'). Ayrıntı: {exc}"
            ) from exc

        embeddings = data.get("embeddings")
        if not embeddings:
            raise OllamaError("Embedding modeli boş sonuç döndürdü.")
        return embeddings
