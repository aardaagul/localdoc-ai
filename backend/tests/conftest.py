"""Pytest ortak kurulumları (fixture'lar).

Not: Ortam değişkenleri, uygulama ayarları ilk kez okunmadan ÖNCE ayarlanır.
Böylece testler gerçek veritabanına ve gerçek Ollama'ya dokunmaz.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

_TMP_DIR = Path(tempfile.mkdtemp(prefix="localdoc-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP_DIR / 'test.db').as_posix()}"
os.environ["DATA_DIR"] = str(_TMP_DIR)
os.environ["UPLOAD_DIR"] = str(_TMP_DIR / "uploads")
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

from fastapi.testclient import TestClient  # noqa: E402

from app.api.deps import get_llm_client  # noqa: E402
from app.db.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from tests.fakes import FakeLLMClient  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_database():
    """Her testten önce temiz bir şema sağlar."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def fake_client() -> FakeLLMClient:
    return FakeLLMClient()


@pytest.fixture
def client(fake_client: FakeLLMClient):
    app.dependency_overrides[get_llm_client] = lambda: fake_client
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
