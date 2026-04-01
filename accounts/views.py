import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile, UserPhoto
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
