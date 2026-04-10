import requests
import random
import urllib3
import math
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from .models import Match, RoommatePreference
from accounts.models import Profile, Verification, UserPhoto

# Terminaldeki SSL uyarılarını gizleme
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# MBTI Havuzumuz
MBTI_TYPES = ['INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 'ENFJ', 'ENFP', 
              'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 'ISTP', 'ISFP', 'ESTP', 'ESFP']

def calculate_cosine_similarity(vec1, vec2):
    """İleriki aşamalar için İki vektör (liste) arasındaki kosinüs benzerliğini hesaplar."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    
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
      
    # LOKASYON BONUSU
    location_bonus = 0
    if profile1.city and profile2.city:
        if profile1.city.lower() == profile2.city.lower():
            location_bonus = 20 # Aynı şehirdeyse ciddi bir avantaj
            
    # Toplam skoru hesapla ve 100 ile sınırla
    final_score = total_score + location_bonus
    return min(final_score, 100)

def generate_bot_users(count=10):
    url = f"https://randomuser.me/api/?results={count}&nat=tr,en,de" # TR, İngiltere ve Almanya karışık gelsin
    response = requests.get(url, verify=False)
    data = response.json()
    
    for item in data['results']:
        first_name = item['name']['first']
        last_name = item['name']['last']
        username = item['login']['username']
        email = item['email']
        city = item['location']['city']
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
        
        # 2. Profil Oluşturma (Zorunlu Eşleştirme Yöntemi)
        mbti = random.choice(MBTI_TYPES)
        bio = f"Selam! Ben {first_name}. {city} şehrinde yaşıyorum. Düzenli ve uyumlu bir ev arkadaşı arıyorum. MBTI tipim {mbti}."
        
        profile, created = Profile.objects.update_or_create(
            user=user,
            defaults={'city': city, 'bio': bio, 'mbti_type': mbti}
        )
        
        # 3. Alt Tabloları Oluşturma
        RoommatePreference.objects.get_or_create(profile=profile)
        Verification.objects.get_or_create(user=user)
        
        # 4. Fotoğraf İndirme ve Profile Bağlama
        img_response = requests.get(picture_url, verify=False)
        if img_response.status_code == 200:
            photo, created = UserPhoto.objects.get_or_create(profile=profile)
            photo.image.save(f"{username}.jpg", ContentFile(img_response.content), save=True)
            
    return True
