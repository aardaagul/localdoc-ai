# LocalDoc AI — Yerel LLM Destekli Doküman Bilgi Sistemi

**Proje türü:** Bireysel veya 2 kişilik yazılım projesi  
**Önerilen süre:** 3–4 hafta  
**Seviye:** Orta-ileri (4/5)  
**Temel yaklaşım:** AI, uygulamanın kendisi değil; dokümanlardan bilgi bulup kaynaklı cevap üreten bir özelliktir.  
**Çalışma biçimi:** LLM ve embedding modeli yerel olarak Ollama üzerinden çalıştırılacaktır.

---

## 1. Projenin amacı

LocalDoc AI, kullanıcıların PDF ve TXT belgelerini yükleyebildiği, bu belgeler hakkında doğal dille soru sorabildiği ve cevapları ilgili kaynaklarla birlikte alabildiği bir web uygulamasıdır.

Örnek kullanım:

1. Kullanıcı bir ders notu veya kulüp yönergesi yükler.
2. Sistem dosyanın metnini çıkarır ve işler.
3. Kullanıcı “Proje tesliminde hangi belgeler gerekiyor?” diye sorar.
4. Sistem soruyla ilişkili metin parçalarını bulur.
5. Yerel LLM, bulunan parçalara dayanarak cevap oluşturur.
6. Arayüz cevabın yanında kaynak dosyayı ve mümkünse sayfa numarasını gösterir.
7. Belgelerde yeterli bilgi yoksa sistem bunu açıkça söyler; bilgi uydurmamalıdır.

Bu proje sırasında geliştiricinin dosya işleme, API tasarımı, veri tabanı, yerel model çalıştırma, embedding, arama, RAG, hata yönetimi ve test konularını öğrenmesi beklenir.

## 2. Projenin sınırları

Bu proje genel amaçlı bir chatbot değildir. Sistem yalnızca kullanıcının yüklediği ve erişim yetkisi bulunan belgelerden cevap üretmeye odaklanır.

### İlk sürümde yapılmayacaklar

- Model eğitimi veya fine-tuning
- Birden fazla kullanıcının aynı belge alanını paylaştığı karmaşık kurumsal yetkilendirme
- İnternette otomatik araştırma
- Görsel, ses ve video analizi
- Agent sistemleri ve araç kullanan otonom ajanlar
- Bulut tabanlı ücretli LLM API'sine bağımlılık
- Karmaşık mikroservis mimarisi

Öncelik küçük ama güvenilir ve uçtan uca çalışan bir ürün çıkarmaktır.

## 3. Temel kavramlar

- **LLM:** Soruyu ve ilgili belge parçalarını kullanarak doğal dilde cevap oluşturan dil modeli.
- **Embedding:** Metinleri anlamsal benzerlik araması yapılabilecek sayısal vektörlere dönüştüren model.
- **Chunk (parça):** Büyük bir belgenin arama ve modele bağlam sağlamak için bölünmüş küçük metin bölümü.
- **Retrieval (getirme):** Soruyla ilişkili belge parçalarını bulma aşaması.
- **RAG (Retrieval-Augmented Generation):** Önce ilgili kaynakları bulup sonra bu kaynaklara dayanarak cevap üretme yaklaşımı.
- **Kaynak/citation:** Cevabın dayandığı dosya, sayfa veya metin parçası.

## 4. Önerilen teknoloji yığını

Teknoloji seçimi geliştirici tarafından gerekçelendirilmelidir. Aşağıdaki yığın bir öneridir:

- **Backend:** Python + FastAPI
- **Yerel model sunucusu:** Ollama
- **LLM:** Bilgisayarın donanımına uygun bir sohbet modeli
- **Embedding modeli:** Ollama üzerinden çalıştırılabilen bir embedding modeli
- **Metin çıkarma:** PDF için uygun bir Python kütüphanesi; TXT için standart dosya okuma
- **Veri tabanı:** SQLite
- **İlk arama yaklaşımı:** Basit anahtar kelime araması
- **İkinci arama yaklaşımı:** Embedding tabanlı anlamsal arama
- **Vektör saklama:** İlk aşamada dosya/SQLite tabanlı basit çözüm veya uygun hafif bir vektör veri tabanı
- **Frontend:** React + TypeScript veya geliştiricinin gerekçelendirdiği benzer bir arayüz
- **Test:** Pytest ve API testleri
- **Versiyon kontrolü:** Git + GitHub

İlk gün tüm teknolojileri eklemek zorunlu değildir. Önce küçük bir uçtan uca akış çalıştırılmalı, ardından bileşenler eklenmelidir.

## 5. Kullanıcı senaryoları

### Senaryo A — Belge yükleme

1. Kullanıcı PDF veya TXT dosyası seçer.
2. Sistem uzantı, dosya boyutu ve okunabilirlik kontrollerini yapar.
3. Dosya kaydedilir.
4. Metin çıkarılır.
5. Metin parçalara bölünür.
6. Belge ve parçalar veri tabanında veya seçilen depolamada saklanır.
7. Arayüz belge durumunu gösterir: `İşleniyor`, `Hazır` veya `Hata`.

### Senaryo B — Belge hakkında soru sorma

1. Kullanıcı bir belge seçer veya erişebildiği belge koleksiyonunda soru sorar.
2. Sistem soruyu alır.
3. İlgili parçaları arar.
4. En alakalı parçalar LLM'e bağlam olarak gönderilir.
5. Model, bağlamla sınırlı bir cevap üretir.
6. Sistem cevapla birlikte kullanılan kaynakları döndürür.
7. Arayüz cevap ve kaynakları gösterir.

### Senaryo C — Cevap bulunamaması

1. Kullanıcı belgelerde yer almayan bir soru sorar.
2. Sistem yeterli ilgili içerik bulamazsa bunu tespit etmeye çalışır.
3. Modelden belgedeki bilgi yetersizse bunu açıkça belirtmesi istenir.
4. Arayüz “Yüklenen belgelerde bu soruyu yanıtlayacak yeterli bilgi bulunamadı” benzeri bir mesaj gösterir.

### Senaryo D — Belgeyi silme

1. Kullanıcı belgeyi siler.
2. Belge kaydı, metin parçaları ve bunlara ait arama/embedding kayıtları temizlenir.
3. Silinen belgenin eski parçaları sonraki cevaplarda kullanılmaz.

## 6. İşlevsel gereksinimler

### 6.1 Belge yönetimi

- PDF ve TXT yükleme
- Dosya adı, boyutu, yüklenme zamanı ve işleme durumu gösterme
- Belge listesini görüntüleme
- Belgeyi silme
- Desteklenmeyen veya bozuk dosyaları anlaşılır hata ile reddetme
- Aynı dosyanın tekrar yüklenmesi durumunu makul biçimde ele alma
- Dosya boyutu için sınır belirleme ve uygulama

### 6.2 Metin çıkarma ve parçalara bölme

- PDF sayfalarından metin çıkarma
- Mümkün olduğunda her parçayla kaynak sayfa numarasını saklama
- Boş veya metin çıkarılamayan PDF'leri tespit etme
- Metni parçalara ayırma
- Parçalar arasında gerektiğinde küçük bir örtüşme (overlap) kullanma
- Parça boyutu ve örtüşme kararlarını dokümante etme
- Her parçayı belge kimliği ve parça sırasıyla ilişkilendirme

Tarama görüntüsü biçimindeki PDF'ler OCR gerektirebilir. OCR ilk sürümde zorunlu değildir; desteklenmiyorsa kullanıcıya açıkça bildirilmelidir.

### 6.3 Soru-cevap

- Kullanıcıdan doğal dilde soru alma
- Belge seçimi veya belge koleksiyonu seçimi
- Soruyla ilişkili kaynak parçaları bulma
- Kaynak parçalarını LLM'e gönderme
- Cevap ve kaynak metaverisini yapılandırılmış biçimde döndürme
- Kaynakların arayüzde açılabilir/görüntülenebilir olması
- Boş soru ve aşırı uzun girdi kontrolleri
- Model yanıt vermediğinde veya zaman aşımına uğradığında hata yönetimi

### 6.4 Arama

Geliştirme iki aşamada yapılmalıdır:

1. **Başlangıç:** Basit anahtar kelime aramasıyla ilgili metin parçalarını bul.
2. **Geliştirme:** Embedding modeliyle anlamsal arama ekle.

Örnek: Belgede “teslim tarihi” yazarken kullanıcı “ödevi ne zamana kadar vermeliyim?” diye sorabilir. Anlamsal arama, kelimeler aynı olmasa bile ilişkili bölümü bulmaya yardımcı olur.

Arama sonuçları alaka düzeyine göre sıralanmalı; kaç parçanın LLM'e gönderileceği geliştirici tarafından seçilip gerekçelendirilmelidir.

### 6.5 Cevap kalitesi ve kaynaklar

- Modelden yalnızca verilen bağlama dayanması istenir.
- Cevapta kullanılan kaynakların kimlikleri uygulama tarafından kontrol edilir.
- Modelin uydurduğu dosya veya sayfa numaraları doğrudan doğru kabul edilmez.
- Kaynak parçaları cevapla birlikte gösterilir.
- Yeterli kaynak yoksa cevap verilmemesi veya belirsizliğin açıklanması sağlanır.
- Modelin hatalı cevap verebileceği README'de belirtilir.

### 6.6 Geçmiş

İlk sürümde en azından son soru-cevap oturumları yerel veri tabanında saklanabilir. Her mesajın hangi belge koleksiyonu veya kaynaklarla ilişkili olduğu belirlenmelidir. Konuşma geçmişi, modelin önceki cevabını kanıt olarak kullanmamalıdır.

## 7. Önerilen veri modeli

Veri modeli geliştirme sırasında değişebilir. Başlangıç için şu tablolar düşünülebilir:

### documents
- `id`
- `filename`
- `stored_path` veya depolama anahtarı
- `file_type`
- `file_size`
- `status`
- `created_at`
- `error_message` (isteğe bağlı)

### document_chunks
- `id`
- `document_id`
- `chunk_index`
- `page_number` (varsa)
- `content`
- embedding verisi veya embedding deposundaki referans

### conversations
- `id`
- `created_at`
- `title` (isteğe bağlı)

### messages
- `id`
- `conversation_id`
- `role`
- `content`
- `created_at`

### message_sources
- `message_id`
- `chunk_id`
- `relevance_score` (arama yöntemi sağlıyorsa)

Geliştirici bu şemayı aynen kopyalamak zorunda değildir; ilişkileri ve seçimlerini açıklamalıdır. Dosya yolu ve kullanıcı girdileri güvenli şekilde ele alınmalıdır.

## 8. Önerilen API uçları

API tasarımı geliştirici tarafından tamamlanmalıdır. Başlangıç önerileri:

- `GET /api/health` — uygulama durumu
- `GET /api/documents` — belgeleri listele
- `POST /api/documents` — belge yükle
- `GET /api/documents/{id}` — belge ayrıntısı ve işleme durumu
- `DELETE /api/documents/{id}` — belgeyi ve ilişkili kayıtları sil
- `POST /api/documents/{id}/reprocess` — belgeyi yeniden işle (opsiyonel)
- `POST /api/questions` — soru gönder ve kaynaklı cevap al
- `GET /api/conversations` — geçmişi listele (opsiyonel)
- `GET /api/conversations/{id}` — konuşma ayrıntısı (opsiyonel)

API, uygun HTTP durum kodları ve anlaşılır hata gövdeleri kullanmalıdır. Uzun süren işlemlerde arayüzün sonsuza kadar beklemesi engellenmelidir.

## 9. Kullanıcı arayüzü

En az şu ekranlar bulunmalıdır:

1. **Belgeler:** Yükleme alanı, belge listesi, durum ve silme işlemi
2. **Belge ayrıntısı:** Dosya metaverisi ve işleme durumu
3. **Soru-cevap:** Soru alanı, cevap alanı ve kaynak listesi
4. **Geçmiş:** Önceki sorular ve cevaplar (kapsama dahil edildiyse)
5. **Hata durumları:** Model kapalı, dosya işlenemedi, cevap bulunamadı gibi durumların açıkça gösterilmesi

Arayüz sade ve kullanılabilir olmalı; yükleme ve model yanıtı sırasında bekleme durumu göstermelidir.

## 10. Yol haritası

### Aşama 0 — Araştırma ve planlama (1–2 gün)

- Ollama'nın ne olduğunu ve yerel model sunucusu olarak nasıl çalıştığını araştır.
- Bilgisayarın RAM/işletim sistemi kapasitesini kontrol et.
- Küçük bir sohbet modeli seç ve indir.
- Terminalden modele örnek bir soru sor.
- Ollama API'sine bir HTTP isteği gönder.
- Bir embedding modelinin ne yaptığını araştır.
- Kısa bir teknik karar belgesi hazırla: seçilen modeller, donanım gereksinimleri, backend/frontend ve veri tabanı tercihleri.

**Teslim:** Araştırma notu ve çalışan yerel model demosu.

### Aşama 1 — Temel uygulama ve model bağlantısı (2–3 gün)

- Git deposunu oluştur.
- Backend iskeletini kur.
- Sağlık kontrolü endpoint'i ekle.
- Backend'den Ollama'ya istek gönder.
- Model cevabını API üzerinden döndür.
- Ollama kapalıysa veya model bulunamazsa anlaşılır hata üret.

**Teslim:** Arayüz veya API üzerinden yerel modele soru sorulabilen minimal demo.

### Aşama 2 — Dosya yükleme ve metin çıkarma (3–4 gün)

- PDF/TXT yüklemeyi ekle.
- Dosya türü ve boyut kontrollerini uygula.
- PDF sayfalarından metin çıkar.
- Metin çıkarılamayan dosyaları ele al.
- Belge kayıtlarını SQLite'a kaydet.
- Belge listesini ve silme işlevini oluştur.

**Teslim:** Kullanıcının belge yükleyip işleme durumunu görebildiği sürüm.

### Aşama 3 — Chunking ve temel arama (2–3 gün)

- Metni parçalara ayır.
- Her parçayı belgeyle ve mümkünse sayfa numarasıyla ilişkilendir.
- İlk olarak anahtar kelime araması uygula.
- Bir soruya uygun birkaç parça getir.
- Arama sonuçlarını ve seçilen kaynakları debug çıktısında incele.

**Teslim:** Soruyla ilişkili metin parçalarını bulan, kaynaklarını kaybedmeyen arama modülü.

### Aşama 4 — RAG ve kaynaklı cevaplar (3–4 gün)

- Soru ve bulunan parçaları Ollama'daki sohbet modeline gönder.
- Model için açık ve sınırları belli bir sistem talimatı yaz.
- Cevapla birlikte kullanılan kaynak kimliklerini döndür.
- Arayüzde cevap ve kaynakları göster.
- Kaynak bulunmadığında belirsizlik/cevap yok davranışını uygula.
- Modelin kaynak uydurmasını önlemek için kaynakları uygulama tarafında eşleştir.

**Teslim:** Kullanıcının yüklediği dokümanlara dayanarak cevap veren ilk uçtan uca sürüm.

### Aşama 5 — Embedding ve anlamsal arama (3–4 gün)

- Embedding kavramını araştır ve not al.
- Ollama üzerinden uygun bir embedding modeli çalıştır.
- Belge parçaları için embedding üret ve sakla.
- Kullanıcı sorusu için embedding üret.
- Vektör benzerliğiyle en alakalı parçaları getir.
- Anahtar kelime aramasıyla anlamsal aramayı örnek sorular üzerinde karşılaştır.
- Seçilen yöntemi ve kısıtlarını dokümante et.

**Teslim:** Aynı anlama gelen farklı ifadeleri de bulabilen anlamsal arama.

### Aşama 6 — Arayüz, geçmiş ve hata yönetimi (2–4 gün)

- Belgeler ekranını tamamla.
- Soru-cevap ekranını tamamla.
- Kaynakları okunabilir biçimde göster.
- Geçmişi ekle (zaman kalırsa).
- Yükleniyor, hata, boş sonuç ve model kapalı durumlarını ele al.
- Silinen belgenin parçalarının ve embedding kayıtlarının da silindiğini doğrula.

**Teslim:** Kullanılabilir ve baştan sona çalışabilen uygulama.

### Aşama 7 — Test, değerlendirme ve paketleme (2–3 gün)

- Küçük bir test doküman seti oluştur.
- Her belge için cevabı bilinen sorular hazırla.
- Belge içinden cevaplanabilen soruları ve cevaplanamayan soruları test et.
- Cevapların kaynakları gerçekten destekleyip desteklemediğini kontrol et.
- Bozuk PDF, boş soru, uzun soru, modelin kapalı olması gibi durumları test et.
- Docker Compose veya açık kurulum talimatları hazırla.
- README, ekran görüntüleri ve bilinen sınırlamaları ekle.
- Kısa bir demo sunumu hazırla.

**Teslim:** Kurulum yönergeleri bulunan, test edilmiş ve gösterime hazır sürüm.

Süreler tahminidir; modelin donanımda çalışması ve öğrencinin önceki deneyimi süreyi değiştirebilir. Öncelik aşama 1–4 ile çalışan temel ürün çıkarmaktır. Embedding ve arayüz iyileştirmeleri bundan sonra yapılmalıdır.

## 11. Test ve değerlendirme planı

Geliştirici en az 15–20 soruluk küçük bir değerlendirme seti hazırlamalıdır:

- Belgeden doğrudan cevaplanan sorular
- Birden fazla bölümden bilgi gerektiren sorular
- Farklı kelimelerle sorulmuş eşdeğer sorular
- Belgelerde yanıtı bulunmayan sorular
- Birbirine benzeyen ama farklı anlam taşıyan sorular

Her soru için beklenen cevap veya gerekli kaynak bölümü kaydedilmelidir. Sonuçlar elle incelenmeli; yalnızca modelin “iyi görünüyor” denilen cevaplarına güvenilmemelidir.

Ölçülebilecek başlıklar:
- İlgili kaynağın bulunma başarısı
- Cevabın kaynakla tutarlılığı
- Kaynaksız sorularda doğru biçimde cevap vermeme
- Ortalama yanıt süresi
- Model ve donanım kaynaklı hatalar

Başlangıçta basit bir değerlendirme tablosu yeterlidir; karmaşık bir otomatik değerlendirme altyapısı zorunlu değildir.

## 12. Güvenlik ve güvenilirlik

- Yalnızca desteklenen dosya türlerini kabul et.
- Dosya boyutu sınırı koy.
- Dosya adlarını doğrudan güvenilir dosya yolu olarak kullanma.
- Kullanıcı metinlerini ve dosya içeriğini güvenilmeyen veri olarak ele al.
- Belgelerdeki “önceki talimatları yok say” gibi metinlerin sistem talimatlarını değiştirmesine izin verme; belge içeriğini talimat değil, incelenecek veri olarak değerlendir.
- Modelin verdiği kaynak numaralarını doğrudan doğru kabul etme; kaynak kimliklerini uygulama kodu belirlesin.
- Hata mesajlarında hassas yerel dosya yollarını veya gereksiz teknik ayrıntıları gösterme.
- Yerel çalışmanın her koşulda otomatik olarak güvenli olduğu varsayılmamalıdır.
- Model cevapları kesin doğru kabul edilmemelidir.

## 13. Git ve geliştirme süreci

- GitHub deposu kullanılmalı.
- Anlamlı commit mesajları yazılmalı.
- Özellikler küçük parçalara ayrılmalı.
- Mümkünse feature branch ve Pull Request kullanılmalı; tek kişi çalışıyorsa en azından düzenli commit geçmişi tutulmalı.
- `.env.example` veya eşdeğer yapılandırma örneği eklenmeli; gizli bilgiler depoya gönderilmemeli.
- Kurulum, test ve çalıştırma adımları README'de bulunmalı.

Örnek commit mesajları:

- `feat: add document upload endpoint`
- `feat: extract text from PDF files`
- `feat: add keyword retrieval`
- `feat: integrate local Ollama model`
- `test: add no-answer evaluation cases`
- `fix: remove chunks when document is deleted`

## 14. AI araçlarını kullanma kuralları

ChatGPT, Copilot veya benzeri AI geliştirme araçlarını kullanmak serbesttir. Araçlar araştırma, hata ayıklama, örnek kod, test taslağı ve mimari alternatifleri için kullanılabilir.

Ancak geliştirici şu konuları kendi cümleleriyle açıklayabilmelidir:

- Ollama ne yapıyor?
- Sohbet modeli ile embedding modeli arasındaki fark nedir?
- Chunking neden gerekli?
- Retrieval ile generation arasındaki fark nedir?
- RAG hangi problemi çözmeye çalışıyor?
- Kaynak gösterimi nasıl doğrulanıyor?
- Model belge dışı bilgi üretirse uygulama nasıl davranıyor?
- Yerel modelin performansı donanıma göre neden değişiyor?

AI tarafından önerilen kod çalıştırılmalı, incelenmeli ve test edilmelidir. Anlaşılamayan kodun projeye eklenmesi başarı sayılmaz.

## 15. Teslim edilecekler

1. GitHub deposu
2. Çalışan uygulama
3. README ve kurulum rehberi
4. Mimari akış diyagramı
5. Veritabanı şeması
6. Seçilen modeller ve donanım gereksinimlerini açıklayan kısa not
7. Test soruları ve değerlendirme sonuçları
8. Ekran görüntüleri veya kısa demo videosu
9. Bilinen kısıtlar ve sonraki geliştirme önerileri

## 16. Kabul kriterleri

Proje aşağıdaki koşullar sağlandığında temel olarak tamamlanmış sayılır:

- [ ] Ollama yerel makinede çalışıyor ve backend modele bağlanabiliyor.
- [ ] Kullanıcı PDF/TXT yükleyebiliyor.
- [ ] Metin çıkarılıp parçalanıyor ve belgeyle ilişkilendiriliyor.
- [ ] Sistem soruyla ilişkili kaynak parçalarını buluyor.
- [ ] Yerel LLM bulunan kaynaklara dayanarak cevap üretiyor.
- [ ] Cevapla birlikte gerçek kaynaklar gösteriliyor.
- [ ] Cevaplanamayan sorularda sistem belirsizliği belirtiyor.
- [ ] Belge silinince ilişkili parçalar da temizleniyor.
- [ ] Temel hata durumları ve kritik akışlar test ediliyor.
- [ ] Kurulum ve kullanım adımları README'de açıklanıyor.
- [ ] Geliştirici sistem mimarisini ve temel kararlarını açıklayabiliyor.

## 17. Bonus özellikler

Temel gereksinimler tamamlandıktan sonra:

- Birden fazla belge koleksiyonu
- Belge içeriğinde anahtar kelime + anlamsal aramayı birleştirme
- Cevap içindeki kaynaklara tıklayınca ilgili sayfayı veya parçayı açma
- OCR ile taranmış PDF desteği
- Konuşma geçmişi üzerinden takip soruları
- Model ve embedding modelini ayarlardan seçme
- Yanıt süresi ve kullanılan parça sayısını gösterme
- Docker ile uygulamayı paketleme
- Basit bir yeniden sıralama (reranking) yaklaşımını deneme

Bonuslar, temel kabul kriterlerinin yerine geçmez.

---

## Son hedef

Proje sonunda geliştirici yalnızca yerel bir modele soru soran bir arayüz yapmış olmayacak. Dosyaları işleyen, arama yapan, ilgili bağlamı seçen, yerel LLM ile cevap üreten, kaynaklarını gösteren ve cevap kalitesini test eden küçük bir **RAG tabanlı doküman bilgi sistemi** geliştirmiş olacak.
