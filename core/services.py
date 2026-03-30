import requests
import random
import math
import random
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from .models import Profile, Match, RoommatePreference, Verification, UserPhoto

def calculate_cosine_similarity(vec1, vec2):
    """İki vektör (liste) arasındaki kosinüs benzerliğini hesaplar."""
    # İç çarpım (Dot product)
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Öklid normları (Euclidean norms)
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

def mbti_to_vector(mbti_str):
    """
    Kategorik MBTI verisini 4 boyutlu sürekli bir vektöre kodlar.
    Ağırlıklar, nötr durumu temsil eden 0 değeri etrafında +1 ve -1 olarak dağıtılmıştır.
    """
    if not mbti_str or len(mbti_str) != 4:
        return [0, 0, 0, 0]
        
    mbti_str = mbti_str.upper()
    vector = []
    
    vector.append(1 if mbti_str[0] == 'E' else -1 if mbti_str[0] == 'I' else 0)
    vector.append(1 if mbti_str[1] == 'S' else -1 if mbti_str[1] == 'N' else 0)
    vector.append(1 if mbti_str[2] == 'T' else -1 if mbti_str[2] == 'F' else 0)
    vector.append(1 if mbti_str[3] == 'J' else -1 if mbti_str[3] == 'P' else 0)
    
    return vector

def generate_match_score(user1_profile, user2_profile):
    """İki kullanıcının yaşam tarzı ağırlıklarını vektör uzayına çekip skoru hesaplar."""
    
    # İki kullanıcının da oyladığı ortak etiketleri (tag) buluyoruz
    tags_user1 = {ul.tag.id: ul.weight for ul in UserLifestyle.objects.filter(profile=user1_profile)}
    tags_user2 = {ul.tag.id: ul.weight for ul in UserLifestyle.objects.filter(profile=user2_profile)}
    
    # Ortak bir vektör uzayı yaratmak için tüm benzersiz etiket ID'lerini birleştiriyoruz
    all_tag_ids = set(tags_user1.keys()).union(set(tags_user2.keys()))
    
    if not all_tag_ids:
        return 0.0 # Hiçbir ortak veri yoksa uyum 0'dır
        
    vector_a = []
    vector_b = []
    
    # Boyutları eşitleyip, eksik verilere nötr değer (3) atayarak vektörleri dolduruyoruz
    for tag_id in all_tag_ids:
        vector_a.append(tags_user1.get(tag_id, 3))
        vector_b.append(tags_user2.get(tag_id, 3))
        
    # Matematiksel benzerliği hesapla (Sonuç 0 ile 1 arasında döner)
    similarity = calculate_cosine_similarity(vector_a, vector_b)
    
    # Yüzdelik skora çevir (%0 - %100)
    final_score = round(similarity * 100, 2)
    
    # Hesaplanan bu sonucu veritabanına yeni bir eşleşme (Match) objesi olarak kaydet
    Match.objects.create(
        user_1=user1_profile.user,
        user_2=user2_profile.user,
        algorithm_score=final_score
    )
    
    return final_score
    
# MBTI Havuzumuz
MBTI_TYPES = ['INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 'ENFJ', 'ENFP', 
              'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 'ISTP', 'ISFP', 'ESTP', 'ESFP']

def generate_bot_users(count=10):
    # RandomUser API'sinden 'count' kadar kişi çekiyoruz
    url = f"https://randomuser.me/api/?results={count}"
    response = requests.get(url)
    data = response.json()
    
    for item in data['results']:
        first_name = item['name']['first']
        last_name = item['name']['last']
        username = item['login']['username']
        email = item['email']
        city = item['location']['city']
        picture_url = item['picture']['large']
        
        # Kullanıcı adı zaten varsa çakışmayı önlemek için sonuna rakam ekle
        if User.objects.filter(username=username).exists():
            username = f"{username}{random.randint(100, 999)}"
            
        # 1. Ana Kullanıcıyı (User) Yarat
        user = User.objects.create_user(
            username=username,
            email=email,
            password="BotPassword123!", # Botların standart şifresi
            first_name=first_name,
            last_name=last_name
        )
        
        # 2. Profili Yarat (Rastgele MBTI ile)
        mbti = random.choice(MBTI_TYPES)
        bio = f"Selam! Ben {first_name}. {city} şehrinde yaşıyorum. Düzenli ve uyumlu bir ev arkadaşı arıyorum. MBTI tipim {mbti}."
        
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'city': city, 'bio': bio, 'mbti_type': mbti}
        )
        
        # 3. Alt Tabloları Yarat (Hata vermemesi için boş olarak)
        RoommatePreference.objects.get_or_create(profile=profile)
        Verification.objects.get_or_create(user=user)
        
        # 4. Profil Fotoğrafını İnternetten İndir ve Kaydet
        img_response = requests.get(picture_url)
        if img_response.status_code == 200:
            photo = UserPhoto(profile=profile)
            # Django'nun ContentFile özelliği ile görseli diske yazıyoruz
            photo.image.save(f"{username}.jpg", ContentFile(img_response.content), save=True)
            
    return True
