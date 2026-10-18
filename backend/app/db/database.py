"""SQLAlchemy motoru, oturumu ve temel sınıfı."""

from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()
settings.ensure_dirs()

_connect_args: dict = {}
if settings.database_url.startswith("sqlite"):
    # FastAPI testleri ve arka plan görevleri için gerekli
    _connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=_connect_args, future=True)

if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):  # noqa: ANN001
        """SQLite'ta yabancı anahtar kısıtlarını (CASCADE/SET NULL) etkinleştirir."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    """İstek başına bir veritabanı oturumu sağlar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Tüm tabloları (yoksa) oluşturur."""
    from app import models  # noqa: F401  (modelleri Base.metadata'ya kaydeder)

    Base.metadata.create_all(bind=engine)
