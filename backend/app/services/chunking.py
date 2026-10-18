"""Metni, arama ve bağlam için küçük parçalara (chunk) bölme."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.services.extraction import PageText


@dataclass
class ChunkDraft:
    """Henüz veritabanına yazılmamış bir metin parçası."""

    index: int
    page_number: int | None
    content: str


def chunk_pages(
    pages: Sequence[PageText],
    *,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[ChunkDraft]:
    """Sayfa metinlerini kelime sınırlarını koruyarak parçalara böler.

    - ``chunk_size`` hedef karakter sayısıdır (yaklaşık).
    - ``overlap`` birbirini izleyen parçalar arasındaki örtüşme (karakter).
    - Her parça, başladığı sayfanın numarasıyla ilişkilendirilir.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size pozitif olmalıdır.")
    overlap = max(0, min(overlap, chunk_size - 1))

    # (kelime, sayfa_numarası) listesi
    words: list[tuple[str, int]] = []
    for page in pages:
        for word in page.text.split():
            words.append((word, page.page_number))

    chunks: list[ChunkDraft] = []
    total = len(words)
    index = 0
    start = 0

    while start < total:
        length = 0
        end = start
        while end < total and length + len(words[end][0]) + 1 <= chunk_size:
            length += len(words[end][0]) + 1
            end += 1
        if end == start:  # tek kelime chunk_size'tan uzun
            end = start + 1

        content = " ".join(word for word, _ in words[start:end]).strip()
        if content:
            chunks.append(
                ChunkDraft(index=index, page_number=words[start][1], content=content)
            )
            index += 1

        if end >= total:
            break

        # Örtüşme için geri sar (en az bir kelime ilerlemeyi garanti et)
        back = 0
        cursor = end
        while cursor > start and back < overlap:
            cursor -= 1
            back += len(words[cursor][0]) + 1
        start = cursor if cursor > start else end

    return chunks
