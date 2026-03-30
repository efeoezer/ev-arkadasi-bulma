# TypeMatch: MBTI Tabanlı Akıllı Ev Arkadaşı Eşleşme Platformu

TypeMatch, kullanıcıların psikolojik profillerini (MBTI) analiz ederek, ev ortamında en yüksek uyumu yakalayabilecekleri ev arkadaşlarını matematiksel bir algoritma ile bulan yeni nesil bir eşleşme platformudur.

##  Projenin Amacı
Sıradan ilan sitelerinin aksine TypeMatch, "Kim nerede yaşıyor?" sorusundan ziyade **"Kim kiminle uyumlu yaşayabilir?"** sorusuna odaklanır. Kullanıcıların yaşam tarzları, enerji yönleri, bilgi işleme ve karar verme mekanizmaları analiz edilerek, potansiyel çatışmalar daha ev arkadaşlığı başlamadan önlenir.

##  Temel Özellikler (V1.0)
- **MBTI Kişilik Analizi:** Sisteme entegre 12 soruluk test ile kullanıcıların psikolojik profillerinin çıkarılması.
- **Dinamik Veri Görselleştirme:** Chart.js kullanılarak 4 eksenli (E/I, S/N, T/F, J/P) Radar Grafiği ile kişisel analizin sunulması.
- **Akıllı Eşleşme Algoritması:** Adaylar arası "Kosinüs Benzerliği" ve yüzde tabanlı eşleşme motoru.
- **Swipe Arayüzü:** Hammer.js ile desteklenen, mobil uyumlu ve sezgisel "Kaydırma" mekanizması.
- **Otomatik Aday Havuzu:** RandomUser API kullanılarak tek tıkla sisteme gerçekçi bot/aday ekleme sistemi.
- **Güvenli Kimlik Doğrulama:** Django Authentication tabanlı oturum yönetimi ve parçalı veritabanı mimarisi (User & Profile ayrımı).

## Kullanılan Teknolojiler
- **Backend:** Python 3.14, Django 6.0.3
- **Frontend:** HTML5, CSS3 (CSS Grid/Flexbox), JavaScript
- **Kütüphaneler:** Chart.js (Grafikler), Hammer.js (Swipe efektleri)
- **Veritabanı:** SQLite (Geliştirme Ortamı)
- **Dış Servisler:** RandomUser API (Aday Üretimi)

## Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda izole bir ortamda çalıştırmak için aşağıdaki adımları sırasıyla terminalinizde uygulayın:

**1. Depoyu Klonlayın:**
```bash
git clone [https://github.com/efeoezer/typematch.git](https://github.com/efeoezer/typematch.git)
cd typematch
```
**2. Sanal Ortamı (Virtual Environment) Kurun ve Aktifleştirin:**

<ins>Mac / Linux İçin:</ins>
```bash
python3 -m venv venv
source venv/bin/activate
```
<ins>Windows İçin:</ins>
```bash
python -m venv venv
venv\Scripts\activate
```
**3. Gerekli Kütüphaneleri Yükleyin:**
```bash
pip install -r requirements.txt
```
**4. Veritabanı Tablolarını İnşa Edin (Migration):**
```bash
python manage.py makemigrations
python manage.py migrate
```
**5. Yönetici (Superuser) Hesabı Oluşturun:
(Bot üretme butonunu görebilmek için gereklidir)**
```bash
python manage.py createsuperuser
```
**5. Yerel Geliştirme Sunucusunu Başlatın:**
```bash
python manage.py runserver
```
Sunucu başarıyla ayağa kalktığında http://127.0.0.1:8000/admin adresi üzerinden yönetim paneline erişebilir veya API uç noktalarını test edebilirsiniz.

## Ekip

Efe Özer, Nisanaz Avara
