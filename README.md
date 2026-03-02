# MBTI Tabanlı Ev Arkadaşı Eşleşme Platformu

Bu proje, MAT132 - Bilgisayar Programlama 2 dersi kapsamında geliştirilen bir web uygulamasıdır. 

Uygulamanın temel amacı, ev veya oda arkadaşı arayan kişileri sadece bütçe ve lokasyon gibi fiziksel kriterlere göre değil, Myers-Briggs (MBTI) kişilik testi sonuçlarına göre eşleştirmektir.

## Özellikler

- **Kullanıcı Yönetimi:** Güvenli kayıt olma, giriş yapma ve şifreleme (Authentication) işlemleri.
- **Profil Sistemi:** Kullanıcıların bütçe, lokasyon ve ev durumlarını belirtebildikleri veri tabanı ilişkili profil altyapısı.
- **Akıllı Eşleştirme:** Kullanıcıların MBTI tiplerini karşılaştırarak bir uyum skoru (match score) üreten arka plan algoritması.
- **Dış Servis Entegrasyonu:** Kullanıcıların kişilik analizleri veya lokasyon doğrulama işlemleri için harici REST API entegrasyonu sağlanacaktır.

## Mimari ve Teknolojiler

Proje, geliştiricilerin bağımsız çalışabilmesi (asenkron çalışma modeli) amacıyla Frontend ve Backend olarak izole iki yapı (decoupled architecture) halinde geliştirilmektedir. Arka plan işlemleri, Nesne Yönelimli Programlama (OOP) mantığıyla tasarlanmıştır.

- **Backend:** Python (Flask / FastAPI)
- **Veritabanı:** PostgreSQL / SQLite
- **Frontend:** HTML / CSS / JavaScript (Bootstrap/Tailwind)
- **Kütüphaneler:** Projede kullanılan kütüphaneler requirements.txt dosyasında listelenmiştir.

## Kurulum ve Çalıştırma

Projeyi lokal ortamınızda test etmek için aşağıdaki adımları izleyebilirsiniz:

1. Depoyu bilgisayarınıza klonlayın:
   git clone https://github.com/efeoezer/ev-arkadasi-bulma.git

2. Proje dizinine gidin:
   cd ev-arkadasi-bulma

3. Python sanal ortamını oluşturun ve aktifleştirin:
   python -m venv venv
   source venv/bin/activate  # Windows için: venv\Scripts\activate

4. Gerekli kütüphaneleri yükleyin:
   pip install -r requirements.txt

5. Uygulamayı başlatın:
   python main.py

## Ekip

- Efe Özer
- Nisanaz Avara
