# Teknik Kararlar ve Gerekçeler

Bu belge, projede verilen önemli teknik kararları ve bunların nedenlerini özetler.

## 1. Neden RAG (Retrieval-Augmented Generation)?

LLM'ler eğitim verilerinde olmayan kuruma/kişiye özel bilgiyi bilemez ve **uydurma (halüsinasyon)** yapabilir.
RAG ile:

- Model yalnızca **belgelerden getirilen bağlama** dayanarak cevap üretir,
- Cevap **kaynak gösterilerek** doğrulanabilir hale gelir,
- Belgeler güncellendiğinde **yeniden eğitim gerekmez**, yalnızca indeks güncellenir.

## 2. Neden yerel (Ollama)?

- **Gizlilik:** Belgeler ve sorgular makineden dışarı çıkmaz.
- **Maliyet:** API ücreti yok.
- **Çevrimdışı çalışma:** İnternet gerekmez.

## 3. Model seçimi ve donanım notu

| Rol | Varsayılan model | Yaklaşık boyut | Not |
| --- | --- | --- | --- |
| Sohbet (cevap üretimi) | `llama3.2` (3B) | ~2 GB | Hafif, Türkçe'de yeterli; CPU'da da çalışır |
| Sohbet (alternatif) | `qwen2.5:3b` | ~2 GB | Benzer boyut, güçlü çok dilli |
| Sohbet (daha kaliteli) | `llama3.1:8b` | ~5 GB | Daha iyi akıl yürütme, daha fazla RAM/VRAM ister |
| Embedding | `nomic-embed-text` | ~275 MB | Anlamsal arama için; hafif ve hızlı |

**Donanım önerisi**

- **Minimum:** 8 GB RAM, modern çok çekirdekli CPU (3B modeller CPU'da çalışır, ancak yavaş).
- **Önerilen:** 16 GB RAM ve 6+ GB VRAM'e sahip GPU (NVIDIA/AMD/Apple Silicon). GPU, ilk yanıt süresini belirgin biçimde düşürür.
- **Disk:** Modeller için ~3–6 GB boş alan.

Model değiştirmek için `backend/.env`:

```env
OLLAMA_CHAT_MODEL=qwen2.5:3b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

> Embedding modelini **değiştirirseniz**, eski parçaların vektörleri yeni modelle uyumsuz olur. Belgeleri **yeniden işleyin** (`POST /api/documents/{id}/reprocess` veya silip yeniden yükleyin).

## 4. Neden SQLite?

- Tek kullanıcılı yerel uygulama için **sıfır kurulum** ve tek dosya.
- Proje, kurulum karmaşıklığını minimumda tutmayı hedefler.
- **Ölçeklenme sınırı:** Çok büyük belge kümeleri veya çok kullanıcı için PostgreSQL + `pgvector` ya da Qdrant/Chroma gibi bir vektör veritabanına geçilmelidir (bkz. "Sonraki adımlar").

## 5. Embedding'lerin saklanması

Vektörler `document_chunks.embedding` sütununda **JSON metni** olarak saklanır ve benzerlik Python'da kosinüs ile hesaplanır.

- **Artı:** Ek vektör veritabanı bağımlılığı yok; küçük/orta ölçek için yeterli.
- **Eksi:** Parça sayısı arttıkça tarama maliyeti doğrusal büyür.

## 6. Hibrit arama

İki sinyali birleştiririz:

1. **Anahtar kelime puanı:** Sorgu kelimelerinin parçada **idf ağırlıklı kapsanma oranı** (0–1). Her zaman çalışır, embedding gerektirmez.
2. **Anlamsal puan:** Kosinüs benzerliği (0–1).

Birleşik puan: `(1 - SEMANTIC_WEIGHT) * anahtar_kelime + SEMANTIC_WEIGHT * anlamsal`.

**"Bilgi yok" kararı:** `best_keyword < MIN_RELEVANCE_SCORE` **ve** `best_semantic < MIN_SEMANTIC_SCORE` ise model çağrılmaz. Bu, hem alakasız sorularda uydurmayı engeller hem de anlamca eşleşen (kelime örtüşmesi olmayan) soruların çalışmasına izin verir.

## 7. Parçalama (chunking) stratejisi

- **Kelime sınırları korunur** (parçalar ortadan kesilmez).
- `CHUNK_SIZE=1000` karakter, `CHUNK_OVERLAP=150` karakter.
- Örtüşme, bir bilginin iki parçaya bölünmesi durumunda kaybolmamasını sağlar.
- Her parça, **başladığı sayfanın numarasıyla** saklanır (kaynak gösterimi için).

## 8. Kaynak (citation) güvenliği

Model, yanıtında `[1]`, `[2]` gibi numaralar kullanır. Uygulama:

- Numaraları **yalnızca o soru için getirilen** parça aralığında kabul eder,
- Model uydurma numara verse bile gösterilen kaynak her zaman **gerçek** dosya/sayfadır,
- Model hiç atıf yapmazsa, o cevap için getirilen parçaların tümü kaynak olarak sunulur.

## 9. Test yaklaşımı

- Testler **Ollama gerektirmez**: `tests/fakes.py` içindeki `FakeLLMClient` deterministik vektörler üretir.
- Ollama HTTP katmanı, `httpx.MockTransport` ile (gerçek ağ olmadan) test edilir.
- Her test **temiz bir veritabanı** ile başlar (`conftest.py`).
- Bu sayede CI, herhangi bir model kurulumu olmadan yeşil çalışır.

## Sonraki Adımlar

1. **Vektör veritabanı:** `pgvector` / Qdrant / Chroma ile anlamsal aramayı ölçeklenebilir hale getirme.
2. **OCR:** Taranmış PDF'ler için `tesseract` / `ocrmypdf` entegrasyonu.
3. **Kimlik doğrulama ve çok kullanıcılılık:** Kullanıcı bazlı belge koleksiyonları.
4. **Yeniden sıralama (reranking):** İlk getirmeden sonra bir cross-encoder ile sıralamayı iyileştirme.
5. **Akış (streaming):** Cevabı token token göstermek için SSE.
6. **Dosya biçimleri:** DOCX, Markdown, CSV desteği.
7. **Değerlendirme otomasyonu:** [evaluation.md](evaluation.md)'deki soruları otomatik çalıştırıp metrik üreten betik.
