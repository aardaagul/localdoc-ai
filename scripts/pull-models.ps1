# LocalDoc AI - Gerekli Ollama modellerini indirir (Windows / PowerShell)
#
# Kullanim:  .\scripts\pull-models.ps1
# Opsiyonel: $env:OLLAMA_CHAT_MODEL / $env:OLLAMA_EMBED_MODEL ile model secin.

$ErrorActionPreference = 'Stop'

$chat  = if ($env:OLLAMA_CHAT_MODEL)  { $env:OLLAMA_CHAT_MODEL }  else { 'llama3.2' }
$embed = if ($env:OLLAMA_EMBED_MODEL) { $env:OLLAMA_EMBED_MODEL } else { 'nomic-embed-text' }

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Error "Ollama bulunamadi. Once https://ollama.com/download adresinden kurun."
}

Write-Host "[1/2] Sohbet modeli indiriliyor: $chat"
ollama pull $chat

Write-Host "[2/2] Embedding modeli indiriliyor: $embed"
ollama pull $embed

Write-Host "Tamamlandi. Modeller hazir."
Write-Host "Ipuclari: 'ollama list' ile kurulu modelleri gorebilirsiniz."
