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

# 16 MBTI Tipinin Standart Açıklamaları
MBTI_DESCRIPTIONS = {
    'INTJ': 'Stratejik ve analitik düşünürler. Her şey için mantıksal bir planları ve sistemleri vardır.',
    'INTP': 'Yenilikçi mucitler, bilginin ve teorilerin ardındaki temel mantığı ararlar.',
    'ENTJ': 'Cesur, hayal gücü geniş ve güçlü liderler. Karşılaştıkları engelleri aşmak için her zaman bir yol bulurlar.',
    'ENTP': 'Zeki ve meraklı düşünürler. Entelektüel zorluklara karşı koyamazlar ve tartışmayı severler.',
    'INFJ': 'Sessiz ve derinden anlayan, ancak son derece ilham verici ve yorulmak bilmez idealistler.',
    'INFP': 'Şiirsel, nazik ve sadık bireyler. Değerlerine bağlıdırlar ve iyi bir amaç uğruna çalışmaya isteklidirler.',
    'ENFJ': 'Karizmatik ve ilham verici liderler. Çevrelerindeki insanların potansiyellerini ortaya çıkarmalarına yardımcı olurlar.',
    'ENFP': 'Hevesli, yaratıcı ve sosyal özgür ruhlar. Her zaman olasılıkları görür ve bağlantılar kurarlar.',
    'ISTJ': 'Pratik ve gerçeklere odaklı bireyler. Güvenilirlikleri ve sorumluluk bilinçleri yüksektir.',
    'ISFJ': 'Çok adanmış ve sıcak koruyucular. Sevdiklerini ve çevrelerini savunmaya her zaman hazırdırlar.',
    'ESTJ': 'Mükemmel yöneticiler. İnsanları, süreçleri ve olayları yönetmede son derece pratiktirler.',
    'ESFJ': 'Son derece ilgili, sosyal ve popüler insanlar. Başkalarının ihtiyaçlarına karşı çok duyarlıdırlar.',
    'ISTP': 'Cesur ve pratik sorun çözücüler. Çevrelerini gözlemleyip araçları ustalıkla kullanırlar.',
    'ISFP': 'Esnek ve estetik algısı yüksek sanatçılar. Anı yaşarlar ve yeni deneyimleri keşfetmeye hazırdırlar.',
    'ESTP': 'Zeki, enerjik ve eylem odaklı insanlar. Risk almayı severler ve pratik sonuçlara odaklanırlar.',
    'ESFP': 'Spontane, enerjik ve hevesli bireyler. Çevrelerindeki insanları neşelendirmeyi iyi bilirler.',
}

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
def profile_view(request):
    """Kullanıcının profil verilerini, güncelleme formunu ve MBTI grafiğini döndürür."""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Kullanıcının mevcut fotoğrafını çek (Varsa)
    current_photo = profile.userphoto_set.first()
    
    # Form Gönderildiyse (POST işlemi) verileri kaydet
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)
        ph_form = PhotoUpdateForm(request.POST, request.FILES, instance=current_photo)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

            if request.FILES.get('image'):
                new_photo = ph_form.save(commit=False)
                new_photo.profile = profile
                new_photo.save()
                
            return redirect('profile')
    else:
        # Form henüz gönderilmediyse mevcut verilerle dolu olarak getir
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
        ph_form = PhotoUpdateForm(instance=current_photo)

    # --- Grafik (Chart.js) Veri Algoritması ---
    mbti_type = profile.mbti_type if profile.mbti_type else "Bilinmiyor"
    
    chart_data = []
    if len(mbti_type) == 4:
        chart_data.append(85 if mbti_type[0] == 'E' else 15)
        chart_data.append(85 if mbti_type[1] == 'S' else 15)
        chart_data.append(85 if mbti_type[2] == 'T' else 15)
        chart_data.append(85 if mbti_type[3] == 'J' else 15)
    else:
        chart_data = [0, 0, 0, 0]

    mbti_description = MBTI_DESCRIPTIONS.get(
        profile.mbti_type, 
        "Kişilik analizinizi görmek ve algoritmanın çalışmasını sağlamak için lütfen önce testi tamamlayın."
    )

    context = {
        'profile': profile,
        'current_photo': current_photo,
        'chart_data': chart_data,
        'u_form': u_form,
        'p_form': p_form,
        'ph_form': ph_form,
        'mbti_description': mbti_description
    }
    return render(request, 'core/profile.html', context)
def logout_view(request):
    """Kullanıcının oturumunu sonlandırır ve giriş/ana sayfaya yönlendirir."""
    logout(request)
    return redirect('/') # Çıkış yapınca ana dizine yönlendir
def dashboard_view(request):
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

    context = {
        'profile': profile,
        'completion_percentage': score,
        'recent_activities': recent_activities,
        'candidates': candidates
    }
    return render(request, 'core/dashboard.html', context)
def generate_bots_view(request):
    if request.user.is_superuser:
        generate_bot_users(10) 
    return redirect('dashboard')
