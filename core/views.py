from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Profile
from .services import generate_match_score

def calculate_match_api(request, user1_id, user2_id):
    """İki kullanıcının eşleşme skorunu hesaplayıp JSON olarak döndüren API uç noktası."""
    # 1. Veritabanından profilleri çek (Kullanıcı yoksa güvenli bir şekilde 404 Not Found döndür)
    profile1 = get_object_or_404(Profile, user_id=user1_id)
    profile2 = get_object_or_404(Profile, user_id=user2_id)
    
    # 2. Servis katmanındaki soyut matematiksel algoritmayı tetikle
    score = generate_match_score(profile1, profile2)
    
    # 3. Sonucu Frontend arayüzünün (veya herhangi bir cihazın) anlayacağı evrensel JSON formatında paketle
    return JsonResponse({
        'status': 'success',
        'user_1': profile1.user.username,
        'user_2': profile2.user.username,
        'match_score_percentage': score,
        'message': 'Kosinüs benzerliği başarıyla hesaplandı ve veritabanına kaydedildi.'
    })
