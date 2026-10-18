"""Soru-cevap ve konuşma geçmişi şemaları."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceRead(BaseModel):
    """Bir cevabın dayandığı kaynak parçası."""

    model_config = ConfigDict(from_attributes=True)

    chunk_id: int | None = None
    document_id: int | None = None
    filename: str | None = None
    page_number: int | None = None
    relevance_score: float | None = None
    snippet: str | None = None


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    document_ids: list[int] | None = Field(
        default=None, description="Yalnızca bu belgelerde ara (boşsa tüm hazır belgeler)."
    )
    conversation_id: int | None = Field(
        default=None, description="Mevcut bir konuşmaya eklemek için kimliği."
    )
    top_k: int | None = Field(default=None, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Soru boş olamaz.")
        return value


class QuestionResponse(BaseModel):
    answer: str
    no_answer: bool
    sources: list[SourceRead]
    conversation_id: int
    message_id: int


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime
    sources: list[SourceRead] = Field(default_factory=list)


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None = None
    created_at: datetime


class ConversationDetail(ConversationRead):
    messages: list[MessageRead] = Field(default_factory=list)
