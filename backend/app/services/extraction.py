"""PDF ve TXT dosyalarından metin çıkarma."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


class ExtractionError(RuntimeError):
    """Metin çıkarma başarısız olduğunda (bozuk/boş dosya vb.) fırlatılır."""


@dataclass
class PageText:
    """Bir sayfadan (veya TXT için tüm dosyadan) çıkarılan metin."""

    page_number: int
    text: str


def extract_pages(path: str | Path, file_type: str) -> list[PageText]:
    """Dosya türüne göre sayfa metinlerini döndürür."""
    file_type = (file_type or "").lower().lstrip(".")
    if file_type == "pdf":
        return _extract_pdf(path)
    if file_type == "txt":
        return _extract_txt(path)
    raise ExtractionError(f"Desteklenmeyen dosya türü: {file_type or 'bilinmiyor'}")


def _extract_pdf(path: str | Path) -> list[PageText]:
    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # noqa: BLE001 - pypdf çok çeşitli hatalar fırlatabilir
        raise ExtractionError("PDF dosyası açılamadı veya bozuk görünüyor.") from exc

    pages: list[PageText] = []
    for number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:  # noqa: BLE001 - tek sayfa hatası tüm dosyayı bozmasın
            text = ""
        pages.append(PageText(page_number=number, text=text))

    if not any(page.text.strip() for page in pages):
        raise ExtractionError(
            "PDF'ten metin çıkarılamadı. Dosya taranmış görüntü olabilir; "
            "OCR bu sürümde desteklenmiyor."
        )
    return pages


def _extract_txt(path: str | Path) -> list[PageText]:
    raw = Path(path).read_bytes()
    for encoding in ("utf-8", "cp1254", "latin-1"):
        try:
            return [PageText(page_number=1, text=raw.decode(encoding))]
        except UnicodeDecodeError:
            continue
    raise ExtractionError("TXT dosyası okunamadı (desteklenmeyen kodlama).")
