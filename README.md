# 📄 LocalDoc AI

**Yerel LLM destekli doküman bilgi sistemi** — PDF ve TXT belgelerinizi yükleyin, belgeleriniz hakkında doğal dille soru sorun, cevapları **kaynaklarıyla** (dosya + sayfa) alın.

> AI burada uygulamanın kendisi değil; **dokümanlardan bilgi bulup kaynaklı cevap üreten** bir özelliktir.
> Tüm model çağrıları (LLM + embedding) **yerel** olarak [Ollama](https://ollama.com) üzerinden yapılır; verileriniz makinenizden dışarı çıkmaz.

[![CI](https://github.com/aardaagul/localdoc-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/aardaagul/localdoc-ai/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6)](https://www.typescriptlang.org/)
[![Ollama](https://img.shields.io/badge/Ollama-yerel%20model-000000)](https://ollama.com/)

---

## ✨ Özellikler

- **Belge yükleme:** PDF ve TXT dosyaları (sürükle-bırak veya seçerek), boyut/tür doğrulaması ile.
- **Metin çıkarma:** `pypdf` ile PDF'ten sayfa bazlı, TXT için kodlama tahminli metin okuma.
- **Akıllı parçalama (chunking):** Örtüşmeli, kelime sınırlarını koruyan parçalama; her parça sayfa numarasıyla saklanır.
- **İki aşamalı arama:**
  1. **Anahtar kelime araması** (idf ağırlıklı, Türkçe + İngilizce stopword temizliği ile) — her zaman çalışır.
  2. **Anlamsal arama** (Ollama embedding + kosinüs benzerliği) — embedding modeli varsa devreye girer.
- **Kaynaklı cevap (RAG):** Yerel sohbet modeli yalnızca getirilen bağlama dayanarak cevap üretir; cevapta `[1]`, `[2]` gibi atıflar kullanılır ve uygulama bunları **gerçek dosya/sayfa** ile eşler.
- **Uydurmaya karşı koruma:** Yeterli bilgi yoksa sistem modeli hiç çağırmadan *"Yüklenen belgelerde bu soruyu yanıtlayacak yeterli bilgi bulunamadı."* der.
- **Sohbet geçmişi:** Konuşmalar ve cevapların kaynakları veritabanında saklanır; arayüzden görüntülenip silinebilir.
- **Zarif bozulma:** Ollama kapalıysa uygulama çökmez; arama çalışır, model gereken yerlerde anlaşılır hata (HTTP 503) döner.

---

## 🏗️ Mimari

```
┌────────────────┐   REST /api    ┌──────────────────┐   HTTP    ┌───────────────────────┐
│  React + TS    │ ─────────────► │  FastAPI Backend │ ────────► │  Ollama (yerel sunucu) │
│  Arayüz (Vite) │ ◄───────────── │  (Python)        │ ◄──────── │  • sohbet modeli       │
└────────────────┘   JSON + CORS  └────────┬─────────┘           │  • embedding modeli    │
                                           │                     └───────────────────────┘
                                   ┌───────┴────────┐
                                   │  SQLite        │  belgeler, parçalar (embedding),
                                   │  + dosya depo  │  konuşmalar, mesaj kaynakları
                                   └────────────────┘
```

Detaylı akış diyagramı, veritabanı şeması ve veri akışı için: **[docs/architecture.md](docs/architecture.md)**

---

## 🧰 Teknoloji Yığını

| Katman | Teknoloji |
| --- | --- |
| Arayüz | React 18 + TypeScript + Vite |
| Backend | Python 3.11+ , FastAPI , SQLAlchemy 2 , Pydantic v2 |
| Veritabanı | SQLite (dosya tabanlı) |
| Metin çıkarma | pypdf (PDF) + yerleşik kodlama tahmini (TXT) |
| Yerel model sunucusu | Ollama (`/api/chat`, `/api/embed`) |
| HTTP istemcisi | httpx |
| Test | pytest + FastAPI TestClient + httpx MockTransport |

Seçim gerekçeleri ve model/donanım önerileri: **[docs/decisions.md](docs/decisions.md)**

---

## 📁 Klasör Yapısı

```
localdoc-ai/
├── backend/                      # FastAPI uygulaması
│   ├── app/
│   │   ├── core/config.py        # Ayarlar (.env + ortam değişkenleri)
│   │   ├── db/database.py        # SQLAlchemy motoru, oturum, init_db
│   │   ├── models/               # documents, document_chunks, conversations, messages, message_sources
│   │   ├── schemas/              # Pydantic istek/yanıt modelleri
│   │   ├── services/
│   │   │   ├── extraction.py     # PDF/TXT -> metin
│   │   │   ├── chunking.py       # metin -> parçalar
│   │   │   ├── ollama_client.py  # Ollama HTTP istemcisi
│   │   │   ├── retrieval.py      # anahtar kelime + anlamsal arama
│   │   │   ├── rag.py            # kaynaklı cevap üretimi
│   │   │   ├── storage.py        # dosya doğrulama/kaydetme
│   │   │   └── processing.py     # belge işleme hattı (arka plan görevi)
│   │   ├── api/routes/           # health, documents, questions, conversations
│   │   └── main.py               # Uygulama girişi
│   ├── tests/                    # pytest testleri (Ollama gerektirmez)
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── Dockerfile
│   └── .env.example
├── frontend/                     # React + TypeScript (Vite) arayüzü
│   ├── src/
│   │   ├── api.ts                # Backend istemcisi
│   │   ├── types.ts              # Tipler
│   │   ├── App.tsx               # Sekmeler (Belgeler / Soru-Cevap / Geçmiş)
│   │   ├── components/           # StatusBadge
│   │   └── pages/                # DocumentsPage, AskPage, HistoryPage
│   ├── vite.config.ts            # /api proxy ayarı
│   ├── Dockerfile / nginx.conf
│   └── .env.example
├── docs/                         # Mimari, kararlar, değerlendirme
├── scripts/                      # Ollama model indirme betikleri
├── docker-compose.yml            # Ollama + Backend + Arayüz
└── LICENSE
```

---

## 🚀 Hızlı Başlangıç

### 0) Gereksinimler

- **Python 3.11+**
- **Node.js 20+** (arayüz için)
- **Ollama** (yerel modeller için) — <https://ollama.com/download>

### 1) Ollama'yı kurun ve modelleri indirin

```bash
# Ollama'yı kurduktan sonra (uygulama arka planda çalışır)
ollama pull llama3.2          # sohbet (cevap üretme) modeli
ollama pull nomic-embed-text  # embedding (anlamsal arama) modeli
```

> Farklı bir model kullanmak isterseniz `.env` içindeki `OLLAMA_CHAT_MODEL` / `OLLAMA_EMBED_MODEL` değerlerini değiştirin.
> Daha hafif bir alternatif: `ollama pull qwen2.5:3b`

Modelleri indirmek için hazır betikler: `scripts/pull-models.ps1` (Windows) veya `scripts/pull-models.sh` (Linux/macOS).

### 2) Backend'i çalıştırın

```bash
cd backend

# Sanal ortam oluşturun
python -m venv .venv

# Etkinleştirin
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Bağımlılıkları kurun
pip install -r requirements.txt

# Ayarları kopyalayın (isteğe bağlı; varsayılanlar çalışır)
copy .env.example .env          # Linux/macOS: cp .env.example .env

# Sunucuyu başlatın
uvicorn app.main:app --reload --port 8000
```

- API: <http://localhost:8000>
- Swagger (interaktif doküman): <http://localhost:8000/docs>
- Sağlık/durum: <http://localhost:8000/api/health>

### 3) Arayüzü çalıştırın

```bash
cd frontend
npm install
npm run dev
```

Arayüz: <http://localhost:5173>

> Vite, `/api` isteklerini otomatik olarak `http://localhost:8000`'e yönlendirir (proxy).
> Farklı bir adres için `frontend/.env` dosyasına `VITE_PROXY_TARGET=http://localhost:8010` yazın.

### 🐳 Docker ile (opsiyonel)

Ollama + backend + arayüzü birlikte ayağa kaldırır:

```bash
docker compose up --build -d

# Modelleri ilk kez indirin (tek seferlik)
docker compose exec ollama ollama pull llama3.2
docker compose exec ollama ollama pull nomic-embed-text
```

Arayüz: <http://localhost:8080> · API: <http://localhost:8000/docs>

---

## 💻 Kullanım

1. **Belgeler** sekmesinden bir PDF/TXT yükleyin. Durum **"İşleniyor…" → "Hazır"** olarak değişir.
2. **Soru-Cevap** sekmesinde sorunuzu yazın (isterseniz arama kapsamını belirli belgelerle sınırlayın).
3. Sistem ilgili parçaları bulur, yerel model **kaynaklı** cevabı üretir; cevabın altında kaynak dosya/sayfalar listelenir.
4. **Geçmiş** sekmesinde önceki konuşmaları ve kaynaklarını görebilirsiniz.

Hazır örnek belge: [`docs/samples/proje-yonergesi.txt`](docs/samples/proje-yonergesi.txt) — örnek sorularla birlikte deneyebilirsiniz.

---

## 🔌 API Uç Noktaları

| Yöntem | Yol | Açıklama |
| --- | --- | --- |
| `GET` | `/api/health` | Uygulama ve Ollama model durumu |
| `GET` | `/api/documents` | Belgeleri listeler |
| `POST` | `/api/documents` | Belge yükler (multipart `file`) |
| `GET` | `/api/documents/{id}` | Belge ayrıntısı (durum, parça sayısı) |
| `POST` | `/api/documents/{id}/reprocess` | Belgeyi yeniden işler |
| `DELETE` | `/api/documents/{id}` | Belgeyi ve parçalarını siler |
| `POST` | `/api/questions` | Soru sorar, kaynaklı cevap döner |
| `GET` | `/api/conversations` | Konuşmaları listeler |
| `GET` | `/api/conversations/{id}` | Konuşma + mesajlar + kaynaklar |
| `DELETE` | `/api/conversations/{id}` | Konuşmayı siler |

**Örnek istek:**

```bash
curl -X POST http://localhost:8000/api/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Proje tesliminde hangi belgeler gerekiyor?"}'
```

**Örnek yanıt:**

```json
{
  "answer": "Proje tesliminde rapor ve sunum dosyası gereklidir [1].",
  "no_answer": false,
  "sources": [
    {
      "chunk_id": 3,
      "document_id": 1,
      "filename": "proje-yonergesi.txt",
      "page_number": 1,
      "relevance_score": 0.62,
      "snippet": "Proje teslimi icin gerekli belgeler: rapor, sunum dosyasi ve kaynak kod arsividir."
    }
  ],
  "conversation_id": 1,
  "message_id": 2
}
```

---

## ✅ Testler

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -q      # Windows
# python -m pytest -q                        # Linux/macOS
```

- Testler **Ollama gerektirmez**: sahte bir model istemcisi (`tests/fakes.py`) kullanılır.
- Kapsam: metin çıkarma, parçalama, anahtar kelime/anlamsal arama, RAG hattı, "bilgi yok" davranışı, Ollama HTTP istemcisi (sahte taşıma katmanı), belge/soru-cevap uç noktaları ve cascade silme.

Arayüz tarafı:

```bash
cd frontend
npm run typecheck     # tsc --noEmit
npm run build         # tip kontrolü + üretim derlemesi
```

---

## 📊 Değerlendirme

Test soruları, beklenen davranış ve sonuç tablosu: **[docs/evaluation.md](docs/evaluation.md)**

---

## ⚠️ Bilinen Kısıtlar

- **OCR yok:** Taranmış (görüntü) PDF'lerden metin çıkarılamaz; sistem bunu hata olarak bildirir.
- **Tek dil ağırlıklı:** Arama ve istemler Türkçe'ye göre ayarlanmıştır.
- **Ölçek:** SQLite tabanlıdır; çok büyük belge kümeleri için vektör veritabanı (ör. pgvector, Qdrant) önerilir.
- **Embedding opsiyoneldir:** `nomic-embed-text` yüklü değilse yalnızca anahtar kelime araması çalışır.
- **Kimlik doğrulama yok:** Tek kullanıcılı yerel kullanım için tasarlanmıştır.

Sonraki geliştirme önerileri için [docs/decisions.md](docs/decisions.md#sonraki-adımlar) bölümüne bakın.

---

## 🤝 Katkı

Katkılar memnuniyetle karşılanır. Lütfen bir *issue* açın veya *pull request* gönderin. Testleri çalıştırmayı ve kod stiline uymayı unutmayın.

## 📜 Lisans

Bu proje **MIT** lisansı ile lisanslanmıştır — ayrıntı için [LICENSE](LICENSE).
