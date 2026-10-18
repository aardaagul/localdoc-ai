"""Ollama istemcisinin HTTP davranışını (sahte taşıma katmanı ile) test eder."""

from __future__ import annotations

import asyncio

import httpx
import pytest

from app.services.ollama_client import OllamaClient, OllamaError


def _client(handler) -> OllamaClient:
    return OllamaClient(transport=httpx.MockTransport(handler))


def test_chat_parses_message_content():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        return httpx.Response(200, json={"message": {"content": "Merhaba [1]"}})

    result = asyncio.run(_client(handler).chat([{"role": "user", "content": "selam"}]))
    assert result == "Merhaba [1]"


def test_embed_parses_embeddings():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/embed"
        return httpx.Response(200, json={"embeddings": [[0.1, 0.2], [0.3, 0.4]]})

    result = asyncio.run(_client(handler).embed(["a", "b"]))
    assert result == [[0.1, 0.2], [0.3, 0.4]]


def test_chat_http_error_raises_ollama_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="model not found")

    with pytest.raises(OllamaError):
        asyncio.run(_client(handler).chat([{"role": "user", "content": "selam"}]))


def test_is_available_false_when_connection_fails():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("bağlantı yok", request=request)

    assert asyncio.run(_client(handler).is_available()) is False


def test_is_available_true_on_200():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"models": []})

    assert asyncio.run(_client(handler).is_available()) is True
