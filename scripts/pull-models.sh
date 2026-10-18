#!/usr/bin/env bash
# LocalDoc AI - Gerekli Ollama modellerini indirir (Linux / macOS)
#
# Kullanim:  ./scripts/pull-models.sh
# Opsiyonel: OLLAMA_CHAT_MODEL / OLLAMA_EMBED_MODEL ortam degiskenleriyle model secin.

set -euo pipefail

CHAT_MODEL="${OLLAMA_CHAT_MODEL:-llama3.2}"
EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Hata: Ollama bulunamadi. Once https://ollama.com/download adresinden kurun." >&2
  exit 1
fi

echo "[1/2] Sohbet modeli indiriliyor: ${CHAT_MODEL}"
ollama pull "${CHAT_MODEL}"

echo "[2/2] Embedding modeli indiriliyor: ${EMBED_MODEL}"
ollama pull "${EMBED_MODEL}"

echo "Tamamlandi. Modeller hazir."
