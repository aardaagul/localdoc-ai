"""Arama (retrieval): anahtar kelime tabanlı ve anlamsal (embedding) arama."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentChunk

_TOKEN_RE = re.compile(r"[0-9a-zA-ZğüşıöçĞÜŞİÖÇ]+", re.UNICODE)

# Türkçe + İngilizce yaygın "anlamsız" kelimeler. Alaka puanını yapay olarak
# şişirmemeleri için aramada yok sayılır.
_STOPWORDS: set[str] = {
    # Türkçe
    "ve", "ile", "için", "bir", "bu", "şu", "o", "da", "de", "mi", "mı", "mu", "mü",
    "ki", "ise", "ne", "neden", "niçin", "nasıl", "hangi", "kim", "kime", "kimi",
    "nerede", "nereye", "ama", "ancak", "fakat", "veya", "ya", "çünkü", "eğer",
    "gibi", "kadar", "daha", "en", "çok", "az", "her", "bazı", "tüm", "var", "yok",
    "olduğu", "olan", "olarak", "olur", "ben", "sen", "biz", "siz", "onlar",
    "benim", "senin", "onun", "bizim", "sizin", "şey", "şeyler", "gerekiyor",
    "gerekli", "lazım", "mi", "midir",
    # İngilizce
    "the", "a", "an", "of", "to", "in", "on", "at", "for", "and", "or", "is",
    "are", "was", "were", "be", "been", "being", "this", "that", "these", "those",
    "it", "its", "as", "by", "with", "from", "what", "which", "who", "whom",
    "when", "where", "why", "how",
}


def tokenize(text: str) -> list[str]:
    """Metni küçük harfli, noktalama ve stopword'lerden arındırılmış kelimelere böler."""
    tokens = _TOKEN_RE.findall((text or "").lower())
    return [token for token in tokens if len(token) > 1 and token not in _STOPWORDS]


@dataclass
class ScoredChunk:
    chunk: DocumentChunk
    score: float
    keyword_score: float
    semantic_score: float


@dataclass
class RetrievalResult:
    chunks: list[ScoredChunk] = field(default_factory=list)
    best_keyword: float = 0.0
    best_semantic: float = 0.0
    total_chunks: int = 0


def _load_chunks(db: Session, document_ids: Sequence[int] | None) -> list[DocumentChunk]:
    stmt = select(DocumentChunk)
    if document_ids:
        stmt = stmt.where(DocumentChunk.document_id.in_(list(document_ids)))
    return list(db.execute(stmt).scalars().all())


def keyword_scores(query: str, chunks: Sequence[DocumentChunk]) -> dict[int, float]:
    """Sorgudaki kelimelerin (idf ile ağırlıklı) kapsanma oranını [0,1] döndürür."""
    query_terms = set(tokenize(query))
    if not query_terms or not chunks:
        return {}

    chunk_terms = {chunk.id: set(tokenize(chunk.content)) for chunk in chunks}
    n = len(chunks)
    df = {
        term: sum(1 for terms in chunk_terms.values() if term in terms)
        for term in query_terms
    }
    idf = {term: math.log(1 + n / (1 + df[term])) for term in query_terms}
    total_weight = sum(idf.values()) or 1.0

    scores: dict[int, float] = {}
    for chunk in chunks:
        terms = chunk_terms[chunk.id]
        if not terms:
            continue
        matched = sum(idf[term] for term in query_terms if term in terms)
        scores[chunk.id] = matched / total_weight
    return scores


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_scores(
    query_embedding: Sequence[float] | None,
    chunks: Sequence[DocumentChunk],
) -> dict[int, float]:
    """Sorgu vektörü ile parça vektörleri arasındaki kosinüs benzerliği [0,1]."""
    if not query_embedding:
        return {}

    scores: dict[int, float] = {}
    for chunk in chunks:
        if not chunk.embedding:
            continue
        try:
            vector = json.loads(chunk.embedding)
        except (TypeError, ValueError):
            continue
        cosine = _cosine(query_embedding, vector)
        scores[chunk.id] = max(0.0, min(1.0, cosine))
    return scores


def retrieve(
    db: Session,
    query: str,
    *,
    document_ids: Sequence[int] | None = None,
    top_k: int = 5,
    query_embedding: Sequence[float] | None = None,
    semantic_weight: float = 0.5,
) -> RetrievalResult:
    """Sorguya en ilgili parçaları, anahtar kelime ve anlamsal puanları birleştirerek döndürür."""
    chunks = _load_chunks(db, document_ids)
    if not chunks:
        return RetrievalResult()

    keyword = keyword_scores(query, chunks)
    semantic = semantic_scores(query_embedding, chunks)
    use_semantic = bool(semantic)

    results: list[ScoredChunk] = []
    for chunk in chunks:
        kw = keyword.get(chunk.id, 0.0)
        sem = semantic.get(chunk.id, 0.0)
        if use_semantic:
            score = (1 - semantic_weight) * kw + semantic_weight * sem
        else:
            score = kw
        if score > 0:
            results.append(
                ScoredChunk(chunk=chunk, score=score, keyword_score=kw, semantic_score=sem)
            )

    results.sort(key=lambda item: (item.score, item.keyword_score), reverse=True)

    return RetrievalResult(
        chunks=results[:top_k],
        best_keyword=max(keyword.values(), default=0.0),
        best_semantic=max(semantic.values(), default=0.0),
        total_chunks=len(chunks),
    )
