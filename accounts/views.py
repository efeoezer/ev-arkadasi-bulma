import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Profile, UserPhoto
from core.models import RoommatePreference
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

@csrf_exempt
def register_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Bu kullanıcı adı zaten sistemde kayıtlı.'}, status=400)

            user = User.objects.create_user(username=username, password=password)
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

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
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
    logout(request)
    return JsonResponse({'status': 'success', 'message': 'Başarıyla çıkış yapıldı.'})

def logout_view(request):
    """Kullanıcının oturumunu sonlandırır ve giriş/ana sayfaya yönlendirir."""
    logout(request)
    return redirect('/')

@login_required
def onboarding_wizard(request):
    """Kullanıcının kayıt olduktan sonra geçtiği adım adım sihirbaz."""
    profile, created = Profile.objects.get_or_create(user=request.user)
    prefs, _ = RoommatePreference.objects.get_or_create(profile=profile)

    if request.method == 'POST':
        # Kimlik Bilgileri
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()

        # Lokasyon ve MBTI (Eğer formda varsa alınır, yoksa boş kalır)
        profile.city = request.POST.get('city', profile.city)
        profile.country = request.POST.get('country', profile.country)
        profile.mbti_type = request.POST.get('mbti_type', profile.mbti_type)
        profile.save()

        # Yaşam Tarzı Tercihleri
        smoking_val = request.POST.get('smoking')
        if smoking_val:
            prefs.smoking_allowed = (smoking_val == 'true')
        
        pet_val = request.POST.get('pet')
        if pet_val:
            prefs.has_pet = (pet_val == 'true')
            
        prefs.save()

        messages.success(request, "Sihirbazı tamamladın! Profilin harika görünüyor.")
        return redirect('dashboard')

    return render(request, 'accounts/onboarding_wizard.html')

@login_required
def profile_view(request):
    """Gelişmiş Profil Görünümü: Ad, Soyad ve Görsel Veriler"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    current_photo = profile.userphoto_set.first()
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)
        ph_form = PhotoUpdateForm(request.POST, request.FILES, instance=current_photo)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

            if request.FILES.get('image'):
                if current_photo:
                    current_photo.delete()
                new_photo = ph_form.save(commit=False)
                new_photo.profile = profile
                new_photo.save()
                
            messages.success(request, "Bilgilerin güncellendi!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
        ph_form = PhotoUpdateForm(instance=current_photo)

    # Grafik (Chart.js) Veri Algoritması
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
        'u_form': u_form,
        'p_form': p_form,
        'ph_form': ph_form,
        'chart_data': chart_data,
        'mbti_description': mbti_description,
    }
    return render(request, 'core/profile.html', context)

@login_required
def delete_photo_view(request):
    """Kullanıcının mevcut profil fotoğrafını veritabanından siler."""
    profile = get_object_or_404(Profile, user=request.user)
    photo = profile.userphoto_set.first()
    if photo:
        photo.delete()
    return redirect('profile')

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('/')
    return render(request, 'core/delete_confirm.html')

@login_required
def mbti_test_view(request):
    """Sadece test sayfasını yükler"""
    return render(request, 'core/mbti_test.html')

@csrf_exempt
@login_required
def save_mbti_api(request):
    """Test sonucunu AJAX ile kaydeden API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mbti_result = data.get('mbti')
            
            if mbti_result:
                profile = request.user.profile
                profile.mbti_type = mbti_result
                profile.save()
                return JsonResponse({'status': 'success', 'message': 'Profil güncellendi!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek'}, status=400)
