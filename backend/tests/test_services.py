"""Metin çıkarma ve parçalama (chunking) servis testleri."""

from __future__ import annotations

import pytest

from app.services.chunking import chunk_pages
from app.services.extraction import ExtractionError, PageText, extract_pages
from tests.utils import make_pdf


def test_extract_txt(tmp_path):
    path = tmp_path / "not.txt"
    path.write_text(
        "Proje teslimi icin gerekli belgeler: rapor ve sunum dosyasidir.",
        encoding="utf-8",
    )
    pages = extract_pages(path, "txt")
    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert "rapor" in pages[0].text


def test_extract_pdf(tmp_path):
    path = tmp_path / "not.pdf"
    path.write_bytes(make_pdf("Proje teslimi icin gerekli belgeler rapor ve sunum"))
    pages = extract_pages(path, "pdf")
    assert len(pages) == 1
    assert "rapor" in pages[0].text


def test_extract_unsupported_type(tmp_path):
    path = tmp_path / "not.md"
    path.write_text("deneme")
    with pytest.raises(ExtractionError):
        extract_pages(path, "md")


def test_chunk_pages_splits_long_text_with_sequential_indexes():
    text = " ".join(f"kelime{i}" for i in range(400))
    chunks = chunk_pages([PageText(1, text)], chunk_size=200, overlap=40)

    assert len(chunks) > 1
    assert [chunk.index for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.page_number == 1 for chunk in chunks)
    # Hiçbir parça hedef boyutu aşırı biçimde geçmemeli (tek kelime toleransı ile)
    assert all(len(chunk.content) <= 200 + 12 for chunk in chunks)


def test_chunk_pages_keeps_start_page_number():
    pages = [PageText(1, "birinci sayfa metni"), PageText(2, "ikinci sayfa metni")]
    chunks = chunk_pages(pages, chunk_size=5000, overlap=0)
    assert len(chunks) == 1
    assert chunks[0].page_number == 1


def test_chunk_pages_overlap_creates_shared_text():
    text = " ".join(f"w{i}" for i in range(200))
    chunks = chunk_pages([PageText(1, text)], chunk_size=150, overlap=50)
    assert len(chunks) >= 2
    # Örtüşme sayesinde ilk parçanın son kelimesi ikinci parçada da görünmeli
    last_word = chunks[0].content.split()[-1]
    assert last_word in chunks[1].content
