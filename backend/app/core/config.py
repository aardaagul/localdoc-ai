"""Uygulama ayarları.

Değerler öncelik sırasına göre şu kaynaklardan okunur:
1. Ortam değişkenleri (Docker/oransal ortam)
2. `backend/.env` dosyası
3. Bu dosyadaki varsayılanlar
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = BACKEND_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Uygulama
    app_name: str = "LocalDoc AI"
    api_prefix: str = "/api"
    debug: bool = False

    # Depolama
    data_dir: Path = DEFAULT_DATA_DIR
    database_url: str = f"sqlite:///{(DEFAULT_DATA_DIR / 'localdoc.db').as_posix()}"
    upload_dir: Path = DEFAULT_DATA_DIR / "uploads"
    max_file_size_mb: int = 20
    allowed_extensions: str = "pdf,txt"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2"
    ollama_embed_model: str = "nomic-embed-text"
    # İlk istekte model belleğe yüklenirken uzun sürebilir; cömert tutuldu.
    ollama_timeout: float = 300.0

    # RAG / arama
    chunk_size: int = 1000
    chunk_overlap: int = 150
    retrieval_top_k: int = 5
    min_relevance_score: float = 0.1
    min_semantic_score: float = 0.5
    semantic_weight: float = 0.5
    max_question_length: int = 2000

    # CORS (virgülle ayrılmış liste, "*" tümüne izin verir)
    cors_origins: str = "*"

    # ---- Türetilmiş yardımcılar ----
    @property
    def allowed_extensions_list(self) -> list[str]:
        return [
            ext.strip().lower().lstrip(".")
            for ext in self.allowed_extensions.split(",")
            if ext.strip()
        ]

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    def ensure_dirs(self) -> None:
        """Veri ve yükleme klasörlerinin var olduğundan emin olur."""
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
