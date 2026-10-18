"""Soru sorma uç noktası ve konuşma geçmişinin kaydedilmesi."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_llm_client
from app.db.database import get_db
from app.models import Conversation, Message, MessageSource
from app.schemas.chat import QuestionRequest, QuestionResponse, SourceRead
from app.services.ollama_client import LLMClient, OllamaError
from app.services.rag import answer_question

router = APIRouter()


@router.post("/questions", response_model=QuestionResponse, summary="Belgelere soru sor")
async def ask_question(
    payload: QuestionRequest,
    db: Session = Depends(get_db),
    client: LLMClient = Depends(get_llm_client),
) -> QuestionResponse:
    # Konuşma verildiyse önce doğrula (RAG'tan önce), böylece boşa iş yapmayız.
    conversation: Conversation | None = None
    if payload.conversation_id is not None:
        conversation = db.get(Conversation, payload.conversation_id)
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Konuşma bulunamadı."
            )

    try:
        result = await answer_question(
            db,
            payload.question,
            client=client,
            document_ids=payload.document_ids,
            top_k=payload.top_k,
        )
    except OllamaError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    if conversation is None:
        conversation = Conversation(title=payload.question[:80])
        db.add(conversation)
        db.flush()

    user_message = Message(conversation_id=conversation.id, role="user", content=payload.question)
    assistant_message = Message(
        conversation_id=conversation.id, role="assistant", content=result.answer
    )
    for source in result.sources:
        assistant_message.sources.append(
            MessageSource(
                chunk_id=source.chunk_id,
                document_id=source.document_id,
                filename=source.filename,
                page_number=source.page_number,
                relevance_score=source.relevance_score,
                snippet=source.snippet,
            )
        )

    db.add_all([user_message, assistant_message])
    db.commit()
    db.refresh(assistant_message)

    return QuestionResponse(
        answer=result.answer,
        no_answer=result.no_answer,
        sources=[SourceRead.model_validate(source) for source in assistant_message.sources],
        conversation_id=conversation.id,
        message_id=assistant_message.id,
    )
