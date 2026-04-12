import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import Profile
from .models import Like, Match
from .services import generate_match_score, generate_bot_users
from chat.models import Message 

def index_view(request):
    return render(request, 'core/index.html')

@login_required
def dashboard(request):
    # 1. TEMEL VERİLER
    profile, created = Profile.objects.get_or_create(user=request.user)
    swiped_user_ids = Like.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)

    # 2. MESAJLARI ÇEK
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).order_by('-sent_at')
    unread_count = unread_messages.count()

    # 3. SENİ BEĞENENLER
    # Senin henüz etkileşime girmediğin (swipe yapmadığın) ama seni beğenenler.
    people_who_liked_me_query = Like.objects.filter(to_user=request.user).exclude(
        from_user__id__in=swiped_user_ids
    ).select_related('from_user__profile')

    # 4. SON AKTİVİTELER VE GİZEMLİ MESAJLAR
    recent_activities = []
    likes_count = people_who_liked_me_query.count()

    # --- Mesaj Bildirimleri ---
    if unread_count > 0:
        recent_activities.append(f"📩 {unread_count} yeni mesajın var! Cevaplamak için sabırsızlanıyorlar.")
    
    if likes_count > 0:
        recent_activities.append(f"Şu an seni bekleyen {likes_count} yeni beğeni var! 🔥")
    
    if not profile.mbti_type:
        recent_activities.append("⚙️ MBTI testini çözerek daha iyi eşleşmeler bulabilirsin.")

    # 5. PROFİL TAMAMLAMA SKORU
    score = 0
    if profile.bio: score += 25
    if profile.city: score += 25
    if profile.mbti_type: score += 25
    if profile.userphoto_set.exists(): score += 25

    # 6. ADAY LİSTESİ VE FİLTRELEME
    selected_city = request.GET.get('city')
    room_style = request.GET.get('room_style')
    max_rent = request.GET.get('max_rent')

    # Eğer şehir seçilmediyse kullanıcının kendi şehrini default yap
    if not selected_city and profile.city:
        selected_city = profile.city

    candidates_query = Profile.objects.exclude(user=request.user).exclude(user__id__in=swiped_user_ids)
    
    if selected_city:
        candidates_query = candidates_query.filter(city=selected_city)
    if room_style:
        candidates_query = candidates_query.filter(preferences__room_type=room_style)
    if max_rent and max_rent.isdigit():
        candidates_query = candidates_query.filter(preferences__max_budget__lte=int(max_rent))

    # Adayları çek ve skorla
    candidates = candidates_query.order_by('-id')[:6]
    for candidate in candidates:
        candidate.match_score = generate_match_score(profile, candidate)

    # 7. MENÜ İÇİN ŞEHİRLER
    all_cities = Profile.objects.exclude(city__isnull=True).exclude(city="").values_list('city', flat=True).distinct().order_by('city')

    return render(request, 'core/dashboard.html', {
        'profile': profile,
        'completion_percentage': score,
        'recent_activities': recent_activities,
        'unread_count': unread_count,
        'candidates': candidates,
        'all_cities': all_cities,
        'selected_city': selected_city,
        'who_liked_me': people_who_liked_me_query[:3], # Sadece ilk 3 kişiyi blurlu göster
    })

@csrf_exempt
@login_required
def swipe_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            target_user = User.objects.get(id=data.get('target_user_id'))
            action = data.get('action')

            if action == 'right':
                Like.objects.get_or_create(from_user=request.user, to_user=target_user)
                is_mutual = Like.objects.filter(from_user=target_user, to_user=request.user).exists()

                if is_mutual:
                    # Burada user_1 ve user_2 olarak düzelttik:
                    Match.objects.get_or_create(user_1=request.user, user_2=target_user, defaults={'algorithm_score': 0})
                    return JsonResponse({'status': 'match', 'matched_name': target_user.first_name or target_user.username})
                
                return JsonResponse({'status': 'success', 'message': 'Beğenildi'})
            
            return JsonResponse({'status': 'success', 'message': 'Geçildi'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def matches_view(request):
    # select_related ile User ve Profile verilerini tek seferde (JOIN) çekiyoruz
    user_matches = Match.objects.filter(
        Q(user_1=request.user) | Q(user_2=request.user)
    ).select_related('user_1__profile', 'user_2__profile')
    
    matched_data = []

    for m in user_matches:
        # Karşı tarafın kim olduğunu belirle
        other_user = m.user_2 if m.user_1 == request.user else m.user_1
        
        # Okunmamış mesajları say
        unread = Message.objects.filter(
            sender=other_user, 
            receiver=request.user, 
            is_read=False
        ).count()
        
        matched_data.append({
            'profile': other_user.profile,
            'unread_count': unread
        })
            
    return render(request, 'core/matches.html', {'matches': matched_data})

@login_required
def mbti_test_view(request):
    return render(request, 'core/mbti_test.html')

@login_required
def make_bots_like_me(request):
    if request.user.is_superuser:
        bots = User.objects.exclude(id=request.user.id).order_by('-id')[:10]
        for bot in bots:
            Like.objects.get_or_create(from_user=bot, to_user=request.user)
    return redirect('dashboard')

def generate_bots_view(request):
    if request.user.is_superuser:
        generate_bot_users(5)
    return redirect('dashboard')

@login_required
def like_user(request, to_user_id):
    to_user = get_object_or_404(User, id=to_user_id)
    
    # 1. Beğeniyi kaydet (Veya varsa güncelle)
    like, created = Like.objects.get_or_create(
        from_user=request.user,
        to_user=to_user
    )

    # 2. KARŞILIKLI BEĞENİ KONTROLÜ (Match Check)
    reverse_like = Like.objects.filter(from_user=to_user, to_user=request.user).exists()

    if reverse_like:
        # Karşılıklı beğeni var! Match oluştur.
        Match.objects.get_or_create(user1=request.user, user2=to_user)
        # Opsiyonel: Burada bir "Eşleştin!" sayfasına yönlendirebilirsin
        return redirect('match_success_view', match_with_id=to_user.id)

    return redirect('dashboard')
