"""Belge yönetimi uç noktaları (yükleme, listeleme, silme, yeniden işleme)."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_llm_client
from app.db.database import get_db
from app.models import Document
from app.schemas.document import DocumentRead
from app.services.ollama_client import LLMClient
from app.services.processing import process_document
from app.services.storage import UploadError, delete_stored_file, save_upload, validate_upload

router = APIRouter()


def _get_or_404(db: Session, document_id: int) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Belge bulunamadı.")
    return document


@router.get("", response_model=list[DocumentRead], summary="Belgeleri listele")
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    stmt = select(Document).order_by(Document.created_at.desc(), Document.id.desc())
    return list(db.execute(stmt).scalars().all())


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Belge yükle (PDF/TXT)",
)
async def upload_document(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    client: LLMClient = Depends(get_llm_client),
) -> Document:
    content = await file.read()
    try:
        extension = validate_upload(file.filename or "", len(content))
    except UploadError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    stored_path, _ = save_upload(extension, content)
    document = Document(
        filename=file.filename or f"belge.{extension}",
        stored_path=str(stored_path),
        file_type=extension,
        file_size=len(content),
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # İşleme arka planda yapılır; arayüz durumu GET ile takip eder.
    background.add_task(process_document, document.id, client)
    return document


@router.get("/{document_id}", response_model=DocumentRead, summary="Belge ayrıntısı")
def get_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    return _get_or_404(db, document_id)


@router.post(
    "/{document_id}/reprocess",
    response_model=DocumentRead,
    summary="Belgeyi yeniden işle",
)
def reprocess_document(
    document_id: int,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    client: LLMClient = Depends(get_llm_client),
) -> Document:
    document = _get_or_404(db, document_id)
    document.status = "processing"
    document.error_message = None
    db.commit()
    db.refresh(document)
    background.add_task(process_document, document.id, client)
    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Belgeyi ve ilişkili parçaları sil",
)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> None:
    document = _get_or_404(db, document_id)
    stored_path = document.stored_path
    db.delete(document)  # parçalar cascade ile silinir
    db.commit()
    delete_stored_file(stored_path)
