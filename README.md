# TypeMatch: Algoritmik Psikometrik Eşleşme Motoru

Bu proje, MAT132 - Bilgisayar Programlama 2 dersi kapsamında geliştirilmiş, veri odaklı bir karar destek ve eşleşme platformudur. Geleneksel eşleşme sistemlerinin aksine TypeMatch, kullanıcıların yaşam tarzı tercihlerini matematiksel vektörler olarak modeller ve **Kosinüs Benzerliği (Cosine Similarity)** algoritması kullanarak en yüksek yönsel uyuma sahip ev arkadaşlarını bulur.

## Mimari ve Teknolojik Altyapı
Proje, sıkı bağlı (tightly coupled) mimariler yerine **Django MVT (Model-View-Template)** mimarisi kullanılarak geliştirilmiştir. Backend ve veri katmanı tamamen izole çalışır ve dış dünyaya RESTful standartlarında JSON formatında yanıt üretir.

- **Backend Framework:** Python / Django
- **Algoritma Motoru:** Lineer Cebir Tabanlı Kosinüs Benzerliği (Cosine Similarity)
- **Veritabanı:** SQLite / PostgreSQL (3NF Normalizasyon standartlarında, ORM tabanlı)
- **Veri Yapıları:** Set Teorisi ve Çok Boyutlu Vektör Uzayları

## Kurulum ve Çalıştırma (Mac / Linux Ortamı)

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
pip install django
```
**4. Veritabanı Tablolarını İnşa Edin (Migration):**
```bash
python manage.py makemigrations
python manage.py migrate
```
**5. Yerel Geliştirme Sunucusunu Başlatın:**
```bash
python manage.py runserver
```
Sunucu başarıyla ayağa kalktığında http://127.0.0.1:8000/admin adresi üzerinden yönetim paneline erişebilir veya API uç noktalarını test edebilirsiniz.

## Ekip

Efe Özer, Nisanaz Avara
