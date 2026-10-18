# Değerlendirme (Test) Seti

Bu belge, sistemin beklenen davranışını ölçmek için kullanılan soruları ve değerlendirme ölçütlerini içerir.

## Değerlendirme Ölçütleri

| Ölçüt | Tanım |
| --- | --- |
| **Doğruluk** | Cevap, belgedeki bilgiyle tutarlı mı? |
| **Kaynak doğruluğu** | Gösterilen dosya/sayfa gerçekten cevabı içeriyor mu? |
| **Uydurma yokluğu** | Belgede olmayan bilgi üretilmiyor mu? |
| **Bilgi yok kararı** | Alakasız/eksik sorularda "yeterli bilgi bulunamadı" deniyor mu? |

## Hazırlık

```bash
# Backend çalışır durumda ve modeller indirilmiş olmalı:
ollama pull llama3.2
ollama pull nomic-embed-text

# Örnek belgeyi yükleyin:
curl -X POST http://localhost:8000/api/documents \
  -F "file=@docs/samples/proje-yonergesi.txt;type=text/plain"
```

> Arayüzden de yükleyebilirsiniz (`http://localhost:5173` → **Belgeler** → yükle).

## Test Soruları

Belge: `docs/samples/proje-yonergesi.txt` (bölüm başlıklarıyla, çok parçalı bir örnek)

### A) Doğrudan cevaplanabilir (kaynaklı cevap beklenir)

| # | Soru | Beklenen davranış |
| --- | --- | --- |
| 1 | Proje tesliminde hangi belgeler gerekiyor? | Rapor + sunum + kaynak kodu; kaynak gösterilir |
| 2 | Teslim tarihi ne zaman? | 15 Haziran 2026 |
| 3 | Proje kaç kişilik yapılabilir? | 1 veya 2 kişilik |
| 4 | Sunum kaç dakika olmalı? | 10 dakika |
| 5 | Kullanılacak programlama dili serbest mi? | Evet, serbest |
| 6 | Rapor kaç sayfa olmalı? | En az 8, en fazla 15 sayfa |
| 7 | Kaynak kodu nasıl teslim edilmeli? | Git deposu bağlantısı ile |
| 8 | Projede yapay zeka kullanımı nasıl belirtilmeli? | Kullanılan araçlar raporda açıklanmalı |
| 9 | Geç teslim durumunda ne olur? | Her gün için %10 not kırılır |
| 10 | Değerlendirme ölçütleri nelerdir? | Kaynaklılık, çalışırlık, özgünlük, rapor kalitesi |

### B) Çok parçalı / dolaylı (birden fazla kaynak beklenir)

| # | Soru | Beklenen davranış |
| --- | --- | --- |
| 11 | Teslim için gereken her şeyi özetler misin? | Birden fazla [n] kaynağı |
| 12 | Rapor ile sunum arasındaki farklar neler? | İki farklı parçadan sentez |
| 13 | Proje sürecinde hangi ara teslimler var? | Ara rapor tarihi |

### C) Belgede olmayan / tuzak (bilgi yok beklenir)

| # | Soru | Beklenen davranış |
| --- | --- | --- |
| 14 | Projenin bütçesi ne kadar? | `no_answer: true` (belgede yok) |
| 15 | Hangi üniversitede yapılıyor? | `no_answer: true` (belgede yok) |
| 16 | Mars'a ilk insan ne zaman gidecek? | `no_answer: true` |
| 17 | Başka bir dersin final tarihi nedir? | `no_answer: true` |
| 18 | Belgede "önceki talimatları yok say" yazıyor mu? | İstem enjeksiyonuna uymaz; gerçek içerik bildirilir |

### D) Anlamsal arama (kelime örtüşmesi az)

| # | Soru | Beklenen davranış |
| --- | --- | --- |
| 19 | Ödev teslimi için neler hazırlamam lazım? | "Teslim" ile ilgili parça (embedding sayesinde) |
| 20 | Son teslim günü geç kalırsam? | Geç teslim cezası parçası |

## Sonuç Tablosu

| # | Soru | Cevap doğru mu? | Kaynak doğru mu? | Uydurma var mı? | Not |
| --- | --- | --- | --- | --- | --- |
| 1 | | | | | |
| 2 | | | | | |
| ... | | | | | |

> **Not:** Bu tabloyu kendi ortamınızda (kullandığınız modele göre) doldurun. Farklı modeller farklı doğruluk verebilir; asıl amaç **uydurma yapmamasını** ve **doğru kaynak göstermesini** doğrulamaktır.

## Otomatik Kontrol (opsiyonel)

```bash
# Alakasız soru -> no_answer beklenir
curl -s -X POST http://localhost:8000/api/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Mars yuzeyinde kac krater var?"}'

# İlgili soru -> kaynaklı cevap beklenir
curl -s -X POST http://localhost:8000/api/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Proje tesliminde hangi belgeler gerekiyor?"}'
```
