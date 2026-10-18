"""Arama (retrieval) servis testleri: anahtar kelime ve anlamsal arama."""

from __future__ import annotations

import json

from app.models import Document, DocumentChunk
from app.services.retrieval import retrieve


def _seed_chunks(db):
    document = Document(
        filename="proje.txt",
        stored_path="/tmp/proje.txt",
        file_type="txt",
        file_size=10,
        status="ready",
    )
    db.add(document)
    db.flush()
    db.add_all(
        [
            DocumentChunk(
                document_id=document.id,
                chunk_index=0,
                page_number=1,
                content="Proje teslimi icin gerekli belgeler: rapor ve sunum dosyasi.",
            ),
            DocumentChunk(
                document_id=document.id,
                chunk_index=1,
                page_number=2,
                content="Hava durumu bugun gunesli olacak, yagmur beklenmiyor.",
            ),
        ]
    )
    db.commit()
    return document


def test_retrieve_prefers_relevant_chunk_by_keyword(db_session):
    _seed_chunks(db_session)

    result = retrieve(db_session, "teslim icin hangi belgeler gerekiyor", top_k=5)

    assert result.chunks
    assert result.chunks[0].chunk.chunk_index == 0
    assert result.best_keyword > 0


def test_retrieve_returns_empty_when_no_terms_match(db_session):
    _seed_chunks(db_session)

    result = retrieve(db_session, "kuantum mekanigi ve gokyuzu renkleri", top_k=5)

    assert result.best_keyword == 0.0
    assert result.chunks == []


def test_retrieve_semantic_uses_embeddings(db_session):
    document = Document(
        filename="semantic.txt",
        stored_path="/tmp/semantic.txt",
        file_type="txt",
        file_size=10,
        status="ready",
    )
    db_session.add(document)
    db_session.flush()

    vector = [1.0, 0.0, 0.0]
    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="tamamen alakasiz kelimeler burada",
        embedding=json.dumps(vector),
    )
    db_session.add(chunk)
    db_session.commit()

    # Anahtar kelime örtüşmesi yok ama sorgu vektörü aynı -> anlamsal benzerlik 1.0
    result = retrieve(db_session, "hiçbir ortak kelime yok burada", top_k=5, query_embedding=vector)

    assert result.best_semantic == 1.0
    assert result.chunks
    assert result.chunks[0].chunk.id == chunk.id
