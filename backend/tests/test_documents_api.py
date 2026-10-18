"""Belge ve soru-cevap API uçtan uca testleri."""

from __future__ import annotations

from app.models import DocumentChunk, MessageSource


def _upload(client, name: str, content: bytes, mime: str = "text/plain"):
    return client.post("/api/documents", files={"file": (name, content, mime)})


def test_upload_txt_document_processes_to_ready(client):
    response = _upload(
        client,
        "proje.txt",
        "Proje teslimi icin gerekli belgeler: rapor ve sunum dosyasi.".encode("utf-8"),
    )
    assert response.status_code == 201
    document = response.json()
    assert document["file_type"] == "txt"
    # Yanıt anında işleme başlar (status: processing), arka plan görevi TestClient
    # ile tamamlanır; bu yüzden ayrıntı sorgusunda "ready" olmalı.
    detail = client.get(f"/api/documents/{document['id']}").json()
    assert detail["status"] == "ready"
    assert detail["chunk_count"] >= 1
    assert detail["error_message"] is None


def test_upload_rejects_unsupported_extension(client):
    response = _upload(client, "zararli.exe", b"MZ\x90\x00", "application/octet-stream")
    assert response.status_code == 400
    assert "Desteklenmeyen" in response.json()["detail"]


def test_upload_rejects_empty_file(client):
    response = _upload(client, "bos.txt", b"")
    assert response.status_code == 400


def test_list_and_get_and_delete_document(client):
    created = _upload(client, "a.txt", b"birinci belge icerigi burada yaziyor.").json()

    listing = client.get("/api/documents").json()
    assert any(item["id"] == created["id"] for item in listing)

    assert client.get(f"/api/documents/{created['id']}").status_code == 200
    assert client.delete(f"/api/documents/{created['id']}").status_code == 204
    assert client.get(f"/api/documents/{created['id']}").status_code == 404


def test_ask_question_creates_conversation_and_history(client):
    _upload(
        client,
        "proje.txt",
        "Proje teslimi icin gerekli belgeler: rapor ve sunum dosyasi.".encode("utf-8"),
    )

    response = client.post(
        "/api/questions",
        json={"question": "Proje tesliminde hangi belgeler gerekli?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["no_answer"] is False
    assert body["sources"]
    assert body["conversation_id"]

    conversations = client.get("/api/conversations").json()
    assert any(item["id"] == body["conversation_id"] for item in conversations)

    detail = client.get(f"/api/conversations/{body['conversation_id']}").json()
    assert [message["role"] for message in detail["messages"]] == ["user", "assistant"]
    assert detail["messages"][1]["sources"]


def test_ask_question_without_documents_returns_no_answer(client):
    response = client.post("/api/questions", json={"question": "Herhangi bir soru?"})
    assert response.status_code == 200
    assert response.json()["no_answer"] is True


def test_empty_question_is_rejected(client):
    response = client.post("/api/questions", json={"question": "   "})
    assert response.status_code == 422


def test_model_down_returns_service_unavailable(client, fake_client):
    fake_client.fail_chat = True
    _upload(client, "proje.txt", b"Proje teslimi icin gerekli belgeler rapor ve sunum.")

    response = client.post(
        "/api/questions", json={"question": "Proje teslimi belgeler neler?"}
    )
    assert response.status_code == 503
    assert "model" in response.json()["detail"].lower()


def test_deleting_document_removes_chunks_and_nulls_sources(client, db_session):
    created = _upload(
        client, "proje.txt", b"Proje teslimi icin gerekli belgeler rapor ve sunum."
    ).json()
    document_id = created["id"]

    client.post("/api/questions", json={"question": "Proje teslimi belgeler neler?"})

    db_session.expire_all()
    assert db_session.query(DocumentChunk).filter_by(document_id=document_id).count() > 0

    assert client.delete(f"/api/documents/{document_id}").status_code == 204

    db_session.expire_all()
    assert db_session.query(DocumentChunk).filter_by(document_id=document_id).count() == 0
    # Geçmiş kaydı korunur ama artık var olmayan chunk'a işaret etmez
    sources = db_session.query(MessageSource).all()
    assert sources
    assert all(source.chunk_id is None for source in sources)
