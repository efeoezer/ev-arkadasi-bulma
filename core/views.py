import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile
from .services import generate_match_score

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
@csrf_exempt
def register_api(request):
    if request.method == 'POST':
        try:
            # Gelen JSON verisini Python sözlüğüne çevir
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            # Kullanıcı adı çakışmasını kontrol et
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Bu kullanıcı adı zaten sistemde kayıtlı.'}, status=400)

            # Şifreyi hashleyerek veritabanına kaydet
            user = User.objects.create_user(username=username, password=password)
            
            # İlişkisel veritabanı gereği boş bir Profile satırı yarat ve bağla
            Profile.objects.create(user=user)

            return JsonResponse({'status': 'success', 'message': 'Kullanıcı ve profil başarıyla oluşturuldu.'}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Geçersiz metod. Sadece POST kabul edilir.'}, status=405)

@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        # Veritabanındaki hashlenmiş şifre ile girilen şifreyi kriptografik olarak karşılaştır
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Oturum (Session) başlat
            login(request, user)
            return JsonResponse({
                'status': 'success', 
                'message': 'Giriş başarılı.', 
                'user_id': user.id,
                'username': user.username
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz kullanıcı adı veya şifre.'}, status=401)
            
    return JsonResponse({'status': 'error', 'message': 'Geçersiz metod. Sadece POST kabul edilir.'}, status=405)

def logout_api(request):
    # Mevcut oturumu sunucu tarafından sonlandır
    logout(request)
    return JsonResponse({'status': 'success', 'message': 'Başarıyla çıkış yapıldı.'})
def index_view(request):
    """Ana sayfa arayüzünü yükler."""
    return render(request, 'core/index.html')
def dashboard(request):
    return render(request, 'core/dashboard.html')
    
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
