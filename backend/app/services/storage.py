"""Yüklenen dosyaların doğrulanması ve güvenli biçimde saklanması."""

from __future__ import annotations

import uuid
from pathlib import Path

from app.core.config import get_settings


class UploadError(ValueError):
    """Dosya yükleme doğrulaması başarısız olduğunda fırlatılır."""


def _extension(filename: str) -> str:
    return Path(filename or "").suffix.lower().lstrip(".")


def validate_upload(filename: str, size: int) -> str:
    """Uzantı ve boyut kurallarını uygular; geçerliyse uzantıyı döndürür."""
    settings = get_settings()
    extension = _extension(filename)
    if extension not in settings.allowed_extensions_list:
        allowed = ", ".join(settings.allowed_extensions_list)
        raise UploadError(
            f"Desteklenmeyen dosya türü: '{extension or 'bilinmiyor'}'. İzin verilen türler: {allowed}."
        )
    if size <= 0:
        raise UploadError("Yüklenen dosya boş olamaz.")
    if size > settings.max_file_size_bytes:
        raise UploadError(
            f"Dosya boyutu sınırı aşıldı (en fazla {settings.max_file_size_mb} MB)."
        )
    return extension


def save_upload(extension: str, content: bytes) -> tuple[Path, str]:
    """Dosyayı rastgele bir adla yükler. (tam_yol, depolanan_ad) döndürür."""
    settings = get_settings()
    settings.ensure_dirs()
    stored_name = f"{uuid.uuid4().hex}.{extension}"
    destination = Path(settings.upload_dir) / stored_name
    destination.write_bytes(content)
    return destination, stored_name


def delete_stored_file(stored_path: str) -> None:
    """Diskteki dosyayı sessizce siler (yoksa yok sayar)."""
    try:
        Path(stored_path).unlink(missing_ok=True)
    except OSError:
        pass
