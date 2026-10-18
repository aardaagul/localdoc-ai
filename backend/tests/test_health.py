"""Sağlık ve kök uç noktası testleri."""


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "LocalDoc AI"


def test_health_reports_ollama_available(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["ollama"]["available"] is True
    assert body["ollama"]["chat_model"]


def test_health_reports_ollama_down(client, fake_client):
    fake_client.available = False
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["ollama"]["available"] is False
