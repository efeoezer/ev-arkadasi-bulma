import requests
import random
import urllib3
import math
from django.db import transaction
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from .models import Match, RoommatePreference
from accounts.models import Profile, Verification, UserPhoto

# Terminaldeki SSL uyarılarını gizleme
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Veri havuzu
MBTI_TYPES = ['INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 'ENFJ', 'ENFP', 
              'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 'ISTP', 'ISFP', 'ESTP', 'ESFP']

ZODIAC_SIGNS = ['Koç', 'Boğa', 'İkizler', 'Yengeç', 'Aslan', 'Başak', 
                'Terazi', 'Akrep', 'Yay', 'Oğlak', 'Kova', 'Balık']

SMOKING_HABITS = ['Asla', 'Sosyal İçici', 'Düzenli İçici']

DIET_CHOICES = [
        ('none', 'Belirtilmemiş'),
        ('omnivore', 'Hepçil (Her şeyi yer)'),
        ('vegetarian', 'Vejetaryen'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pesketaryen')
    ]



def calculate_cosine_similarity(vec1, vec2):
    """İleriki aşamalar için İki vektör (liste) arasındaki kosinüs benzerliğini hesaplar."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(a * a for a in vec2))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

def generate_match_score(profile1, profile2):
    """
    MBTI teorisine dayalı ağırlıklı uyum skoru.
    N/S (Dünyayı algılama) uyumu en kritik olanıdır.
    """
    if not profile1.mbti_type or not profile2.mbti_type:
        return 0
        
    p1 = profile1.mbti_type.upper()
    p2 = profile2.mbti_type.upper()
    
    # Ağırlıklar: N/S (%40), E/I (%20), T/F (%20), J/P (%20)
    weights = [20, 40, 20, 20] 
    total_score = 0
    
    for i in range(4):
        if p1[i] == p2[i]:
            total_score += weights[i]
            
    # Eğer her şey zıtsa (Tam Zıtların Uyumu), 
    # fiziksel çekim/tamamlayıcılık için taban bir puan verilebilir (%10)
    if total_score == 0:
        total_score = 10
      
    # Mutfak uyumu (Bonus 10 Puan)
    if profile1.diet_preference == profile2.diet_preference:
      total_score += 10
    # Zıt kutuplar için küçük bir tolerans (Opsiyonel)
    elif (profile1.diet_preference == 'vegan' and profile2.diet_preference == 'vegetarian'):
        total_score += 5
       
      
    # LOKASYON BONUSU
    location_bonus = 0
    if profile1.city and profile2.city:
        if profile1.city.lower() == profile2.city.lower():
            location_bonus = 20 # Aynı şehirdeyse ciddi bir avantaj
       
    # Toplam skoru hesapla ve 100 ile sınırla
    final_score = total_score + location_bonus
    return min(final_score, 100)


    def generate_match_score(user1, user2):
    # 1. Kullanıcıların tercih bilgilerini çekiyoruz
    pref1 = getattr(user1, 'preferences', None)
    pref2 = getattr(user2, 'preferences', None)
    
    # Tercihler tanımlanmamışsa varsayılan bir başlangıç puanı verelim
    if not pref1 or not pref2:
        return 0.0

    # ---------------------------------------------------------
    # KRİTİK ALAN KONTROLÜ: Temizlik Seviyesi (1 - 5 Skalası)
    # ---------------------------------------------------------
    cleanliness_diff = abs(pref1.cleanliness_level - pref2.cleanliness_level)
    
    # Senaryo A: Katı Filtreleme (Hard Filter)
    # Temizlik takıntısı 5 olan biri ile 1 veya 2 olan birini kesinlikle eşleştirme!
    if cleanliness_diff >= 3:
        return 0.0  # Puanı sıfıra çekerek eşleşme listesinden eliyoruz.

    # ---------------------------------------------------------
    # NORMAL ALGORİTMA HESAPLAMASI (Kosinüs Benzerliği veya MBTI)
    # ---------------------------------------------------------
    # Örnek başlangıç puanı hesaplama (MBTI ve diğer testler üzerinden)
    base_score = calculate_mbti_and_lifestyle_score(user1, user2)

    # ---------------------------------------------------------
    # Senaryo B: Ceza Puanı (Penalty)
    # Fark tam olarak 2 ise (Örn: 3 ve 5), uyum fena değildir ama yine de sorun çıkabilir.
    # Genel skordan %15 veya sabit 15 puan ceza kırıyoruz.
    if cleanliness_diff == 2:
        base_score = base_score * 0.85  # %15 ceza uygula
        # Alternatif olarak: base_score -= 15

    # ---------------------------------------------------------
    # Ekstra Kontrol: Temizlik Sıklığı (Haftalık Temizlik)
    # ---------------------------------------------------------
    freq_diff = abs(pref1.cleaning_frequency - pref2.cleaning_frequency)
    if freq_diff >= 4:  # Biri haftada 5 kere temizliyor, diğeri hiç (1)
        base_score = base_score * 0.90  # %10 ek ceza

    # Skorun 0 ile 100 arasında kalmasını garanti altına alıyoruz
    return max(0.0, min(float(base_score), 100.0))

def generate_bot_users(count=10):
    url = f"https://randomuser.me/api/?results={count}&nat=tr,gb,de" # gb = İngiltere (en yerine gb daha iyi sonuç verir)
    response = requests.get(url, verify=False)
    data = response.json()
    
    for item in data['results']:
        try:
            with transaction.atomic(): # Her bot için tek bir işlem başlat
                first_name = item['name']['first']
                last_name = item['name']['last']
                username = item['login']['username']
                email = item['email']
                city = item['location']['city']
                country = item['location']['country'] # YENİ: API'den ülkeyi çekiyoruz
                picture_url = item['picture']['large']
                
                if User.objects.filter(username=username).exists():
                    username = f"{username}{random.randint(100, 999)}"
                    
                # 1. User Oluşturma
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="BotPassword123!",
                    first_name=first_name,
                    last_name=last_name
                )
                
                # 2. Profil Oluşturma (Güncellenmiş Profile model alanlarıyla)
                mbti = random.choice(MBTI_TYPES)
                bio = f"Selam! Ben {first_name}. {city}, {country} lokasyonunda yaşıyorum. MBTI tipim {mbti}."
                
                pet = random.choice([True, False, False]) # %33 ihtimalle kedi/köpeği var
                allergy = random.choice([True, False, False, False]) # %25 ihtimalle alerjisi var
                diet = random.choice([choice[0] for choice in DIET_CHOICES])
                smoking = random.choice([True, False])
                cleaning = random.choice(['DAILY', 'WEEKLY', 'BIWEEKLY', 'RELAXED'])
                guest = random.choice(['NO_GUESTS', 'WEEKENDS', 'ANYTIME'])
                sleep = random.choice(['EARLY_BIRD', 'NIGHT_OWL', 'FLEXIBLE'])
                
                profile = Profile.objects.create(
                    user=user,
                    city=city,
                    country=country,
                    mbti_type=mbti,
                    diet_preference=diet,
                    has_pet=pet,
                    has_allergy=allergy,
                    smoking_allowed=smoking,
                    cleaning_frequency=cleaning,
                    guest_policy=guest,
                    sleep_schedule=sleep,
                    budget_limit=random.randint(5000, 25000),
                )
                profile.bio = bio
                profile.save()
                
                # 3. Alt Tablolar (Oto-yaratım)
                RoommatePreference.objects.create(profile=profile)
                Verification.objects.get_or_create(user=user)
                
                # 4. Fotoğraf İşlemi
                img_response = requests.get(picture_url, verify=False)
                if img_response.status_code == 200:
                    photo = UserPhoto.objects.create(profile=profile)
                    photo.image.save(f"{username}.jpg", ContentFile(img_response.content), save=True)
                
                print(f"✅ Bot başarıyla oluşturuldu: {username} ({country})")
                
        except Exception as e:
            print(f"❌ Bot oluşturulurken hata: {e}")
            continue # Hata olursa o botu atla, bir sonrakine geç

    return True

def get_icebreaker_prompts(user1_profile, user2_profile):
    prompts = []
    
    # 1. MBTI Temelli Sorular
    if user1_profile.mbti_type == user2_profile.mbti_type:
        prompts.append(f"İkiniz de {user1_profile.mbti_type} tipisiniz! Evin kuralları konusunda ne kadar titizsiniz?")
    
    # 2. Ortak Yaşam Tarzı (RoommatePreference üzerinden)
    pref1 = getattr(user1_profile, 'preferences', None)
    pref2 = getattr(user2_profile, 'preferences', None)
    
    if pref1 and pref2:
        if pref1.has_pet and pref2.has_pet:
            prompts.append("İkinizin de evcil hayvanı var! Onları tanıştırmaya ne dersiniz?")
        if pref1.dietary_preference == pref2.dietary_preference and pref1.dietary_preference != 'none':
            prompts.append(f"İkiniz de {pref1.get_dietary_preference_display()} besleniyorsunuz. Ortak yemek yapmak harika olabilir!")

    # Eğer hiçbir ortak nokta yoksa genel bir soru
    if not prompts:
        prompts.append("Ev arkadaşlığından en büyük beklentiniz nedir?")
        
    return prompts[:3] # En iyi 3 öneriyi döndür
