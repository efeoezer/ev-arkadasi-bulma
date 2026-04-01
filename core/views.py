import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile, Like, UserPhoto
from .services import generate_match_score, generate_bot_users
from .forms import UserUpdateForm, ProfileUpdateForm, PhotoUpdateForm

def calculate_match_api(request, user1_id, user2_id):
    """İki kullanıcının eşleşme skorunu hesaplayıp JSON olarak döndüren API uç noktası."""
    try:
        # 1. Veritabanından profilleri çek (Kullanıcı yoksa güvenli bir şekilde 404 Not Found döndür)
        profile1 = get_object_or_404(Profile, user_id=user1_id)
        profile2 = get_object_or_404(Profile, user_id=user2_id)
        
        # 2. Servis katmanındaki soyut matematiksel algoritmayı tetikle
        score = generate_match_score(profile1, profile2)
        
        # 3. Sonucu Frontend arayüzünün anlayacağı evrensel JSON formatında paketle
        return JsonResponse({
            'status': 'success',
            'user_1': profile1.user.username,
            'user1_mbti': profile1.mbti_type,
            'user_2': profile2.user.username,
            'user2_mbti': profile2.mbti_type,
            'match_score_percentage': score,
            'message': 'Kosinüs benzerliği başarıyla hesaplandı ve veritabanına kaydedildi.'
        })
    except Exception as e:
        # Beklenmeyen bir hata durumunda kontrollü yanıt dön
        return JsonResponse({
            'status': 'error', 
            'message': f'Hesaplama sırasında bir hata oluştu: {str(e)}'
        }, status=500)

def index_view(request):
    """Ana sayfa arayüzünü yükler."""
    return render(request, 'core/index.html')

@login_required 
def save_mbti_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            final_mbti = data.get('mbti')
            
            if not final_mbti:
                return JsonResponse({'status': 'error', 'message': 'Veri eksik!'}, status=400)

            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.mbti_type = final_mbti
            profile.save()

            return JsonResponse({'status': 'success', 'message': f'Kişilik tipin {final_mbti} olarak kaydedildi!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Geçersiz metod.'}, status=405)
def mbti_test_view(request):
    # Kullanıcı testi çözmek istediğinde bu sayfayı göstereceğiz
    return render(request, 'core/mbti_test.html')

@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # 1. Profil Tamamlama Yüzdesi Hesaplama (Algoritma)
    # Hangi alanlar doluysa puan ekliyoruz
    score = 0
    if profile.bio: score += 25
    if profile.city: score += 25
    if profile.mbti_type: score += 25
    # Bir de fotoğrafı varsa (UserPhoto tablosuna bakıyoruz)
    if profile.userphoto_set.exists(): score += 25
    
    # 2. Son Aktiviteleri Çekme
    # Son 3 eşleşme veya beğeni (Like) bilgisini alıyoruz
    recent_activities = []
    likes = Like.objects.filter(to_user=request.user).order_by('-created_at')[:3]
    for like in likes:
        recent_activities.append(f"👀 {like.from_user.username} profilini beğendi!")
    
    if not profile.mbti_type:
        recent_activities.append("⚙️ MBTI testini henüz çözmedin.")
        
    candidates = Profile.objects.exclude(user=request.user).order_by('-id')[:6]

    for candidate in candidates:
        candidate.match_score = generate_match_score(profile, candidate)

    # --- RÖNTGEN KODLARI BAŞLANGIÇ ---
    print("=== SİSTEM RÖNTGENİ ===")
    print(f"1. Veritabanındaki Toplam Kullanıcı (User): {User.objects.count()}")
    print(f"2. Veritabanındaki Toplam Profil (Profile): {Profile.objects.count()}")
    print(f"3. Arayüze Gönderilen Aday Sayısı: {candidates.count()}")
    print("=======================")
    # --- RÖNTGEN KODLARI BİTİŞ ---

    context = {
        'profile': profile,
        'completion_percentage': score,
        'recent_activities': recent_activities,
        'candidates': candidates
    }
    return render(request, 'core/dashboard.html', context)
def generate_bots_view(request):
    print("--- 1. BOT ÜRETME BUTONUNA BASILDI ---")
    
    if request.user.is_superuser:
        print("--- 2. KULLANICI ADMİN. FONKSİYON BAŞLIYOR ---")
        try:
            # Hızlı test için şimdilik 10 yerine 3 kişi üretelim
            generate_bot_users(3) 
            print("--- 3. İŞLEM BAŞARIYLA TAMAMLANDI! ---")
        except Exception as e:
            print(f"--- KRİTİK HATA: {e} ---")
    else:
        print("--- HATA: Kullanıcı yetkili değil (Superuser değil) ---")
        
    return redirect('dashboard')
    
