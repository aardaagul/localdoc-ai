"""Konuşma geçmişi uç noktaları."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Conversation
from app.schemas.chat import ConversationDetail, ConversationRead

router = APIRouter()


@router.get("", response_model=list[ConversationRead], summary="Konuşmaları listele")
def list_conversations(db: Session = Depends(get_db)) -> list[Conversation]:
    stmt = select(Conversation).order_by(Conversation.created_at.desc(), Conversation.id.desc())
    return list(db.execute(stmt).scalars().all())


@router.get("/{conversation_id}", response_model=ConversationDetail, summary="Konuşma ayrıntısı")
def get_conversation(conversation_id: int, db: Session = Depends(get_db)) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Konuşma bulunamadı.")
    return conversation


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Konuşmayı sil",
)
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)) -> None:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Konuşma bulunamadı.")
    db.delete(conversation)
    db.commit()
