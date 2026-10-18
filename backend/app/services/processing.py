"""Belge işleme hattı: metin çıkarma -> parçalama -> embedding -> durum güncelleme.

Bu fonksiyon FastAPI ``BackgroundTasks`` ile çağrılır ve kendi veritabanı
oturumunu açar (istek oturumu kapanmış olabilir).
"""

from __future__ import annotations

import asyncio
import json

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.models import Document, DocumentChunk
from app.services.chunking import chunk_pages
from app.services.extraction import ExtractionError, extract_pages
from app.services.ollama_client import LLMClient, OllamaError


def process_document(document_id: int, client: LLMClient) -> None:
    """Belgeyi metne çevirir, parçalara böler ve mümkünse embedding'lerini üretir."""
    settings = get_settings()
    db = SessionLocal()
    try:
        document = db.get(Document, document_id)
        if document is None:
            return

        try:
            pages = extract_pages(document.stored_path, document.file_type)
            drafts = chunk_pages(
                pages,
                chunk_size=settings.chunk_size,
                overlap=settings.chunk_overlap,
            )
            if not drafts:
                raise ExtractionError("Belgeden anlamlı bir metin parçası oluşturulamadı.")

            # Embedding üretimi opsiyoneldir: model kapalıysa yalnızca
            # anahtar kelime aramasıyla devam edilir.
            embeddings: list[list[float]] | None = None
            try:
                embeddings = asyncio.run(client.embed([draft.content for draft in drafts]))
            except OllamaError:
                embeddings = None

            document.chunks.clear()
            for draft in drafts:
                embedding_json = None
                if embeddings and draft.index < len(embeddings):
                    embedding_json = json.dumps(embeddings[draft.index])
                document.chunks.append(
                    DocumentChunk(
                        chunk_index=draft.index,
                        page_number=draft.page_number,
                        content=draft.content,
                        embedding=embedding_json,
                    )
                )

            document.chunk_count = len(drafts)
            document.status = "ready"
            document.error_message = None
        except ExtractionError as exc:
            document.status = "error"
            document.error_message = str(exc)
        except Exception as exc:  # noqa: BLE001 - beklenmeyen hatalar da duruma yansımalı
            document.status = "error"
            document.error_message = f"Belge işlenemedi: {exc}"

        db.commit()
    finally:
        db.close()
