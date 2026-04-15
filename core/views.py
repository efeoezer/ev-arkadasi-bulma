import json, random
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import Profile
from .models import Like, Match, Negotiation
from .services import generate_match_score, generate_bot_users
from chat.models import Message 

def index_view(request):
    return render(request, 'core/index.html')

@login_required
def dashboard(request):
    # 1. TEMEL VERİLER
    profile, created = Profile.objects.get_or_create(user=request.user)
    swiped_user_ids = Like.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)

    # Kontrol
    if not profile.is_onboarded:
        return redirect('onboarding')

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
    room_style = request.GET.get('room_style')
    max_rent = request.GET.get('max_rent')

    selected_city = request.GET.get('city', '')
    
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
                    Match.objects.get_or_create(user_1=request.user, user_2=target_user, defaults={'algorithm_score': 0})
                    return JsonResponse({'status': 'match',
                                         'matched_name': target_user.first_name or target_user.username,
                                         'target_user_id': target_user.id
                                        })
                
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
            'unread_count': unread,
            'match_id': m.id
        })
            
    return render(request, 'core/matches.html', {'matches': matched_data})

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
    
    # 1. Beğeniyi kaydet
    like, created = Like.objects.get_or_create(
        from_user=request.user,
        to_user=to_user
    )

    # 2. Karşılıklı beğeni kontrolü
    reverse_like = Like.objects.filter(from_user=to_user, to_user=request.user).exists()

    if reverse_like:
        match_obj, created = Match.objects.get_or_create(
            user_1=request.user, 
            user_2=to_user, 
            defaults={'algorithm_score': 0}
        )
        return redirect('negotiation_board', match_id=match_obj.id)

    return redirect('dashboard')

@login_required
def match_success_view(request, match_with_id):
    """Görkemli eşleşme kutlamasını gösteren ana ekran"""
    matched_with = get_object_or_404(User, id=match_with_id)
    
    # Eşleşme objesini buluyoruz (ID'sini butona koymak için)
    match_obj = Match.objects.filter(
        (Q(user_1=request.user) & Q(user_2=matched_with)) | 
        (Q(user_1=matched_with) & Q(user_2=request.user))
    ).first()

    return render(request, 'core/match_success.html', {
        'matched_with': matched_with,
        'match': match_obj  # Buton linki için gerekli
    })

@login_required
def negotiation_board_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    opponent = match.user_2 if match.user_1 == request.user else match.user_1
    
    return render(request, 'core/negotiation_board.html', {
        'match': match,
        'opponent': opponent
    })

@login_required
def delete_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    if request.user == match.user_1 or request.user == match.user_2:
        match.delete()
    
    return redirect('matches')

@csrf_exempt
@login_required
def api_negotiation(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    if request.user.id != match.user_1.id and request.user.id != match.user_2.id:
        return JsonResponse({'status': 'error', 'message': 'Bu masaya erişim yetkiniz yok.'}, status=403)

    nego, created = Negotiation.objects.get_or_create(match=match)
    is_user1 = (request.user.id == match.user_1.id)
    
    # Karşı taraf BOT ise (veya test için otomatik doldurulması gerekiyorsa)
    opponent_user = match.user_2 if is_user1 else match.user_1
    opponent_ready = nego.user2_ready if is_user1 else nego.user1_ready
    
    # EĞER KARŞI TARAF BİR BOTSA (is_superuser falan üretimi ise) OTOMATİK SEÇİM YAPAR
    # Gerçek kullanıcıysa bu bloğu atlar ve bekler!
    if not opponent_ready and getattr(opponent_user, 'is_bot', True): # is_bot yoksa True sayıp bot simülasyonu yapar (Test için)
        bot_choices = {}
        options = {
            'cleaning': ['Her Gün', 'Haftalık', 'Gevşek'],
            'guests': ['Yasak', 'Haberli İzin', 'Serbest'],
            'noise': ['Sıfır Tolerans', 'Normal', 'Farketmez'],
            'pets': ['Yasak', 'Kafes', 'Serbest']
        }
        for k, v in options.items():
            bot_choices[k] = {'choice': random.choice(v), 'is_ultimatum': random.random() < 0.2, 'status': 'pending'}
        
        if is_user1:
            nego.user2_choices = bot_choices
            nego.user2_ready = True
        else:
            nego.user1_choices = bot_choices
            nego.user1_ready = True
        nego.save()

    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'lock_choices':
            choices = data.get('choices')
            # Başlangıçta tüm kuralların statüsü 'pending' (beklemede) olur
            for k in choices: choices[k]['status'] = 'pending'
            
            if is_user1:
                nego.user1_choices = choices
                nego.user1_ready = True
            else:
                nego.user2_choices = choices
                nego.user2_ready = True
            nego.save()
            return JsonResponse({'status': 'locked'})
            
        elif action == 'resolve_conflict':
            # Kriz çözüldüğünde (Taviz, Koz, Orta Yol) sözleşmeye yazılır
            rule_id = data.get('rule_id')
            res_type = data.get('resolution_type')
            final_val = data.get('final_value')
            
            my_choices = nego.user1_choices if is_user1 else nego.user2_choices
            
            if res_type == 'koz':
                if is_user1: nego.user1_goodwill -= 1
                else: nego.user2_goodwill -= 1
            elif res_type == 'taviz':
                if is_user1: nego.user1_goodwill += 1
                else: nego.user2_goodwill += 1
                
            my_choices[rule_id]['status'] = 'resolved'
            my_choices[rule_id]['final_choice'] = final_val
            
            if is_user1: nego.user1_choices = my_choices
            else: nego.user2_choices = my_choices
            nego.save()
            
            return JsonResponse({'status': 'resolved', 'goodwill': nego.user1_goodwill if is_user1 else nego.user2_goodwill})

        elif action == 'walk_away':
            match.delete()
            return JsonResponse({'status': 'destroyed'})

    # GET İsteği
    return JsonResponse({
        'user_ready': nego.user1_ready if is_user1 else nego.user2_ready,
        'opponent_ready': nego.user2_ready if is_user1 else nego.user1_ready,
        'my_choices': nego.user1_choices if is_user1 else nego.user2_choices,
        'opp_choices': nego.user2_choices if is_user1 else nego.user1_choices,
        'goodwill': nego.user1_goodwill if is_user1 else nego.user2_goodwill
    })
