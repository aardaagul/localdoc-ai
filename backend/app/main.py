"""FastAPI uygulamasının giriş noktası."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import conversations, documents, health, questions
from app.core.config import get_settings
from app.db.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Uygulama başlarken tabloların var olduğundan emin ol.
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Yerel LLM (Ollama) destekli, kaynaklı cevap üreten doküman bilgi sistemi. "
        "PDF/TXT yükleyin, belgeleriniz hakkında soru sorun, cevapları kaynaklarıyla görün."
    ),
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_api = settings.api_prefix
app.include_router(health.router, prefix=_api, tags=["Durum"])
app.include_router(documents.router, prefix=f"{_api}/documents", tags=["Belgeler"])
app.include_router(questions.router, prefix=_api, tags=["Sorular"])
app.include_router(conversations.router, prefix=f"{_api}/conversations", tags=["Geçmiş"])


@app.get("/", tags=["Durum"], summary="Kök")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "health": f"{_api}/health",
    }
