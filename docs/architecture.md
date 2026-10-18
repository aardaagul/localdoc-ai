# Mimari ve Veri Akışı

## 1. Bileşenler

| Bileşen | Sorumluluk |
| --- | --- |
| **Arayüz (React + TS)** | Belge yükleme, soru sorma, cevap + kaynak gösterimi, geçmiş yönetimi |
| **Backend (FastAPI)** | Dosya doğrulama/saklama, metin çıkarma, parçalama, arama, RAG hattı, REST API |
| **Ollama** | Yerel **sohbet** modeli (cevap üretimi) ve **embedding** modeli (anlamsal arama) |
| **SQLite + dosya deposu** | Belgeler, parçalar(+embedding), konuşmalar, mesajlar, mesaj kaynakları, yüklenen dosyalar |

## 2. Genel Akış

```mermaid
flowchart LR
    U[Kullanıcı / Tarayıcı] -->|HTTP| FE[React + TypeScript Arayüz]
    FE -->|REST /api| BE[FastAPI Backend]
    BE -->|SQL| DB[(SQLite)]
    BE -->|dizin| FS[(Yüklenen Dosyalar)]
    BE -->|/api/chat| OL[Ollama]
    BE -->|/api/embed| OL
    OL --> CM[Sohbet Modeli<br/>ör. llama3.2]
    OL --> EM[Embedding Modeli<br/>ör. nomic-embed-text]
```

## 3. Belge Yükleme ve İşleme (indeksleme)

```mermaid
sequenceDiagram
    actor U as Kullanıcı
    participant FE as Arayüz
    participant BE as Backend
    participant DB as SQLite
    participant OL as Ollama

    U->>FE: PDF/TXT seçer
    FE->>BE: POST /api/documents (multipart)
    BE->>BE: Uzantı + boyut doğrulaması
    BE->>BE: Dosyayı rastgele adla diske yazar
    BE->>DB: documents kaydı (status = processing)
    BE-->>FE: 201 { id, status: processing }
    Note over BE: Arka plan görevi (BackgroundTasks)
    BE->>BE: Metin çıkarma (pypdf / TXT)
    BE->>BE: Parçalama (chunk + overlap, sayfa no)
    BE->>OL: POST /api/embed (parça metinleri)
    OL-->>BE: vektörler
    BE->>DB: document_chunks (metin + embedding) yazar,
    BE->>DB: status = ready | error
    loop Arayüz periyodik yenileme
        FE->>BE: GET /api/documents/{id}
        BE-->>FE: status
    end
```

> Embedding modeli kapalıysa işleme **yine tamamlanır** (`status = ready`), ancak parçalar embedding'siz kalır ve yalnızca anahtar kelime araması çalışır.

## 4. Soru-Cevap (RAG) Akışı

```mermaid
sequenceDiagram
    actor U as Kullanıcı
    participant FE as Arayüz
    participant BE as Backend
    participant DB as SQLite
    participant OL as Ollama

    U->>FE: Soru yazar
    FE->>BE: POST /api/questions { question, document_ids? }
    BE->>OL: POST /api/embed (soru)
    OL-->>BE: sorgu vektörü (yoksa atlanır)
    BE->>DB: Aday parçaları yükle
    BE->>BE: Anahtar kelime (idf) + anlamsal (kosinüs) puanları birleştir
    alt Yeterli kanıt yok
        BE-->>FE: no_answer = true, sources = []
    else Yeterli kanıt var
        BE->>OL: POST /api/chat (sistem istemi + numaralı bağlam)
        OL-->>BE: cevap (ör. "... [1]")
        BE->>BE: [n] atıflarını doğrula ve gerçek kaynaklara eşle
        BE->>DB: user + assistant mesajları ve message_sources kaydet
        BE-->>FE: answer + sources + conversation_id
    end
    FE-->>U: Cevap ve kaynaklar (dosya + sayfa)
```

**Önemli davranışlar**

- **Kaynak güvenliği:** Model cevabında `[1]`, `[2]` gibi beklediğimiz referansları üretir. Uygulama **yalnızca geçerli numaraları** kabul eder; model uydursa bile gösterilen kaynaklar her zaman gerçek parçalardır. Model hiç atıf yapmazsa, o cevap için getirilen tüm parçalar kaynak olarak sunulur.
- **"Bilgi yok" durumu:** Getirilen en iyi parçanın anahtar kelime puanı `MIN_RELEVANCE_SCORE` altında **ve** anlamsal puanı `MIN_SEMANTIC_SCORE` altında ise model **hiç çağrılmaz** ve doğrudan "yeterli bilgi bulunamadı" yanıtı üretilir.
- **İstem enjeksiyonuna karşı not:** Sistem istemi, bağlam parçalarının *veri* olduğunu, içlerindeki "talimat" benzeri ifadelerin **uygulanmaması** gerektiğini açıkça belirtir.

## 5. Veritabanı Şeması

```mermaid
erDiagram
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : "sahip (CASCADE)"
    CONVERSATIONS ||--o{ MESSAGES : "sahip (CASCADE)"
    MESSAGES ||--o{ MESSAGE_SOURCES : "sahip (CASCADE)"
    DOCUMENT_CHUNKS ||--o{ MESSAGE_SOURCES : "chunk_id (SET NULL)"

    DOCUMENTS {
        int id PK
        string filename
        string stored_path
        string file_type "pdf|txt"
        int file_size
        string status "processing|ready|error"
        text error_message
        int chunk_count
        datetime created_at
    }

    DOCUMENT_CHUNKS {
        int id PK
        int document_id FK
        int chunk_index
        int page_number
        text content
        text embedding "JSON vektör"
    }

    CONVERSATIONS {
        int id PK
        string title
        datetime created_at
    }

    MESSAGES {
        int id PK
        int conversation_id FK
        string role "user|assistant"
        text content
        datetime created_at
    }

    MESSAGE_SOURCES {
        int id PK
        int message_id FK
        int chunk_id FK "NULL olabilir"
        int document_id
        string filename
        int page_number
        float relevance_score
        text snippet
    }
```

**Silme davranışı**

- Bir belge silindiğinde parçaları **CASCADE** ile silinir.
- Geçmiş kayıtları korunur: `message_sources.chunk_id` **SET NULL** olur; dosya adı/sayfa/parça metni `message_sources` içinde saklandığı için geçmiş hâlâ okunabilir.
- (SQLite'ta bu davranış için bağlantıda `PRAGMA foreign_keys=ON` etkindir.)

## 6. Yapılandırma Önceliği

`backend/app/core/config.py` ayarları şu sırayla okur:

1. **Ortam değişkenleri** (Docker / CI / kabuk)
2. **`backend/.env`** dosyası
3. Koddaki varsayılanlar

Ayrıntılı liste için [`backend/.env.example`](../backend/.env.example).
