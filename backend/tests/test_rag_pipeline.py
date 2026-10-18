"""RAG hattı testleri (sahte model istemcisi ile)."""

from __future__ import annotations

import asyncio

from app.models import Document, DocumentChunk
from app.services.rag import NO_ANSWER_TEXT, answer_question


def _seed_document(db) -> Document:
    document = Document(
        filename="proje.txt",
        stored_path="/tmp/proje.txt",
        file_type="txt",
        file_size=10,
        status="ready",
    )
    db.add(document)
    db.flush()
    db.add(
        DocumentChunk(
            document_id=document.id,
            chunk_index=0,
            page_number=1,
            content="Proje teslimi icin gerekli belgeler: rapor ve sunum dosyasi.",
        )
    )
    db.commit()
    return document


def test_answer_question_returns_answer_and_sources(db_session, fake_client):
    _seed_document(db_session)

    result = asyncio.run(
        answer_question(
            db_session,
            "Proje tesliminde hangi belgeler gerekli?",
            client=fake_client,
        )
    )

    assert result.no_answer is False
    assert result.answer.startswith("Sahte cevap")
    assert len(result.sources) == 1
    assert result.sources[0].filename == "proje.txt"
    assert result.sources[0].page_number == 1
    assert fake_client.chat_calls  # model gerçekten çağrıldı


def test_no_answer_when_documents_irrelevant(db_session, fake_client):
    _seed_document(db_session)

    result = asyncio.run(
        answer_question(
            db_session,
            "Mars'a insan ne zaman gonderilecek?",
            client=fake_client,
        )
    )

    assert result.no_answer is True
    assert result.answer == NO_ANSWER_TEXT
    assert result.sources == []
    assert fake_client.chat_calls == []  # gereksiz model çağrısı yapılmadı


def test_answer_question_works_without_embeddings(db_session, fake_client):
    fake_client.fail_embed = True  # embedding modeli kapalı -> sadece anahtar kelime araması
    _seed_document(db_session)

    result = asyncio.run(
        answer_question(db_session, "teslim belgeler rapor", client=fake_client)
    )

    assert result.no_answer is False
    assert result.sources


def test_model_no_answer_text_is_respected(db_session, fake_client):
    fake_client.chat_reply = NO_ANSWER_TEXT
    _seed_document(db_session)

    result = asyncio.run(
        answer_question(db_session, "teslim belgeler rapor", client=fake_client)
    )

    assert result.no_answer is True
    assert result.sources == []
