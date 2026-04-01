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
    Şu anki aşama için MBTI üzerinden 4 eksenli (yüzdelik) uyum skoru üretir.
    Her ortak harf %25 uyum puanı kazandırır.
    """
    if not profile1.mbti_type or not profile2.mbti_type:
        return 0
        
    mbti1 = profile1.mbti_type.upper()
    mbti2 = profile2.mbti_type.upper()
    
    if len(mbti1) != 4 or len(mbti2) != 4:
        return 0
        
    score = 0
    # 4 ekseni (E/I, S/N, T/F, J/P) sırasıyla karşılaştır
    for i in range(4):
        if mbti1[i] == mbti2[i]:
            score += 25
            
    return score

def generate_bot_users(count=10):
    url = f"https://randomuser.me/api/?results={count}"
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
