import json, random
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import Profile
from .models import Like, Match, Negotiation
from .services import generate_match_score, generate_bot_users
from chat.models import Message 

TR_MAP = {
    'DAILY': 'Her Gün', 'WEEKLY': 'Haftada Bir', 'BIWEEKLY': 'İki Haftada Bir', 'RELAXED': 'Kirlendikçe',
    'NO_GUESTS': 'Kesinlikle Yasak', 'WEEKENDS': 'Sadece Hafta Sonu', 'ANYTIME': 'Haberli Her Zaman',
    'EARLY_BIRD': 'Erkenci (12 Öncesi)', 'NIGHT_OWL': 'Gece Kuşu', 'FLEXIBLE': 'Esnek',
    'True': 'Kabul', 'False': 'İstenmiyor', True: 'Kabul', False: 'İstenmiyor'
}

def get_tr(val):
    return TR_MAP.get(str(val), str(val))

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
    
    if not profile.budget_limit:
        return redirect('edit_lifestyle')

    # 2. MESAJLARI ÇEK
    unread_messages = Message.objects.filter(
        conversation__participants=request.user, 
        is_read=False
    ).exclude(sender=request.user).order_by('-created_at')
    unread_count = unread_messages.count()

    # 3. SENİ BEĞENENLER
    people_who_liked_me_query = Like.objects.filter(to_user=request.user).exclude(
        from_user__id__in=swiped_user_ids
    ).select_related('from_user__profile')

    # 4. SON AKTİVİTELER VE GİZEMLİ MESAJLAR
    recent_activities = []
    likes_count = people_who_liked_me_query.count()

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

    # 6. ADAY LİSTESİ VE ZENGİN FİLTRELEME MOTORU
    candidates_query = Profile.objects.exclude(user=request.user).exclude(user__id__in=swiped_user_ids)
    
    # Şehir Filtresi
    selected_city = request.GET.get('city', '')
    if selected_city:
        candidates_query = candidates_query.filter(city=selected_city)
        
    # Oda/Ev Tipi Filtresi
    room_style = request.GET.get('room_style')
    if room_style:
        try:
            candidates_query = candidates_query.filter(room_type=room_style)
        except Exception:
            pass

    # Bütçe Filtresi (Çökme hatası düzeltildi: Modeldeki alan budget_limit olarak geçiyor)
    max_rent = request.GET.get('max_rent')
    if max_rent and max_rent.isdigit():
        try:
            candidates_query = candidates_query.filter(budget_limit__lte=int(max_rent))
        except Exception:
            pass

    # MBTI Filtresi
    mbti = request.GET.get('mbti')
    if mbti:
        candidates_query = candidates_query.filter(mbti_type=mbti)

    # Beslenme (Diyet) Filtresi
    diet = request.GET.get('diet')
    if diet:
        candidates_query = candidates_query.filter(diet_preference=diet)

    # Sigara Filtresi
    smoking = request.GET.get('smoking')
    if smoking == 'True':
        try:
            candidates_query = candidates_query.filter(smoking_allowed=True)
        except Exception:
            pass
    elif smoking == 'False':
        try:
            candidates_query = candidates_query.filter(smoking_allowed=False)
        except Exception:
            pass

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
        'who_liked_me': people_who_liked_me_query[:5], 
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
                    match_obj, created = Match.objects.get_or_create(user_1=request.user, user_2=target_user, defaults={'algorithm_score': 0})
                    return JsonResponse({'status': 'match',
                                         'matched_name': target_user.first_name or target_user.username,
                                         'target_user_id': target_user.id,
                                         'match_id': match_obj.id
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
            conversation__participants=request.user,
            sender=other_user, 
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
def delete_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    if request.user == match.user_1 or request.user == match.user_2:
        match.delete()
    
    return redirect('matches')

def get_middle(key, v1, v2):
    if key == 'rent': return f"{(int(v1) + int(v2)) // 2} TL"
    if key == 'cleaning': return "Nöbetleşe Ortak Temizlik"
    if key == 'guest': return "Sadece Hafta Sonu (Haberli)"
    if key == 'sleep': return "Gece 01:00 Sonrası Sessizlik"
    if key == 'smoking': return "Sadece Açık Alan / Balkon"
    if key == 'pets': return "Sadece Kendi Odasında"
    return "Orta Yol"

def resolve_matrix(key, c1, c2, v1, v2):
    if c1 == 'force' and c2 == 'force': return 'BOOM', 'deadlock'
    if c1 == 'force': return v1, 'user1_won'
    if c2 == 'force': return v2, 'user2_won'
    if c1 == 'yield' and c2 == 'yield': return get_middle(key, v1, v2), 'mutual_middle'
    if c1 == 'middle' and c2 == 'yield': return v1, 'user1_won_soft'
    if c2 == 'middle' and c1 == 'yield': return v2, 'user2_won_soft'
    return get_middle(key, v1, v2), 'mutual_middle'

def generate_veto_conflicts(p1, p2):
    rules = {
        'rent': ('Kira Bütçesi', p1.budget_limit or 10000, p2.budget_limit or 10000),
        'cleaning': ('Temizlik Sıklığı', p1.cleaning_frequency, p2.cleaning_frequency),
        'guest': ('Misafir Kuralı', p1.guest_policy, p2.guest_policy),
        'sleep': ('Uyku Düzeni', p1.sleep_schedule, p2.sleep_schedule),
        'smoking': ('Sigara', p1.smoking_allowed, p2.smoking_allowed),
        'pets': ('Evcil Hayvan', p1.pets_allowed, p2.pets_allowed),
    }
    
    conflicts = {}
    has_pending = False
    for key, (name, val1, val2) in rules.items():
        tr_v1 = f"{val1} TL" if key == 'rent' else get_tr(val1)
        tr_v2 = f"{val2} TL" if key == 'rent' else get_tr(val2)

        if val1 == val2:
            conflicts[key] = {'name': name, 'p1': tr_v1, 'p2': tr_v2, 'middle': tr_v1, 'status': 'resolved', 'final': tr_v1, 'winner': 'mutual'}
        else:
            conflicts[key] = {'name': name, 'p1': tr_v1, 'p2': tr_v2, 'middle': get_middle(key, val1, val2), 'status': 'pending'}
            has_pending = True
            
    return conflicts, has_pending

@login_required
def negotiation_board(request, match_id):
    match = Match.objects.filter(id=match_id).first()
    if not match:
        return redirect('dashboard')

    is_user1 = (request.user == match.user_1)
    other_user = match.user_2 if is_user1 else match.user_1
    negotiation, created = Negotiation.objects.get_or_create(match=match)

    if created:
        conflicts, _ = generate_veto_conflicts(match.user_1.profile, match.user_2.profile)
        negotiation.current_offer = conflicts
        negotiation.status = 'ONGOING'
        # Her iki tarafa 2 başlangıç kozu veriyoruz
        negotiation.user1_koz = 2 
        negotiation.user2_koz = 2
        negotiation.current_turn = random.choice([match.user_1, match.user_2])
        negotiation.save()

    # ==========================================
    # BOT YAPAY ZEKASI (Mini Karar Motoru)
    # ==========================================
    if negotiation.status == 'ONGOING' and 'bot' in negotiation.current_turn.username.lower():
        conflicts = negotiation.current_offer
        pending_keys = [k for k, v in conflicts.items() if v['status'] == 'pending']
        
        if pending_keys:
            # Bot rastgele bir kriz maddesi seçer
            key = random.choice(pending_keys)
            data = conflicts[key]
            is_bot_user1 = (negotiation.current_turn == match.user_1)
            bot_koz = negotiation.user1_koz if is_bot_user1 else negotiation.user2_koz
            
            # Botun kozu varsa %50 ihtimalle sana ŞART DAYATIR
            if bot_koz > 0 and random.choice([True, False]):
                if is_bot_user1:
                    data['final'] = data['p1']; data['winner'] = 'u1'; negotiation.user1_koz -= 1
                else:
                    data['final'] = data['p2']; data['winner'] = 'u2'; negotiation.user2_koz -= 1
            else: 
                # Kozu yoksa veya kullanmak istemezse TAVİZ VERİR
                if is_bot_user1:
                    data['final'] = data['p2']; data['winner'] = 'u2'; negotiation.user1_koz += 1
                else:
                    data['final'] = data['p1']; data['winner'] = 'u1'; negotiation.user2_koz += 1
            
            data['status'] = 'resolved'
            
            # Tüm pürüzler çözüldü mü?
            if not any(v['status'] == 'pending' for v in conflicts.values()):
                negotiation.status = 'ACCEPTED'
            else:
                # Oynamasını bitirdi, sırayı sana salıyor
                negotiation.current_turn = request.user
            
            negotiation.save()

    # ==========================================
    # KULLANICI HAMLESİ (Normal POST işlemleri)
    # ==========================================

    if request.method == "POST":
        action = request.POST.get('action')
        
        # 1. Masayı Devirme (Her zaman aktif)
        if action == 'walk_away':
            negotiation.status = 'FAILED'
            negotiation.save()
            return redirect('negotiation_board', match_id=match_id)

        # 2. Hamle Yapma (Sadece sıra sendeyse)
        if negotiation.status == 'ONGOING' and negotiation.current_turn == request.user:
            conflicts = negotiation.current_offer
            
            if action == 'submit_move':
                for key, data in conflicts.items():
                    if data['status'] == 'pending':
                        decision = request.POST.get(f'decision_{key}')
                        if decision == 'force': # Koz Kullan
                            if is_user1 and negotiation.user1_koz > 0:
                                data['final'] = data['p1']; data['status'] = 'resolved'; data['winner'] = 'u1'; negotiation.user1_koz -= 1
                            elif not is_user1 and negotiation.user2_koz > 0:
                                data['final'] = data['p2']; data['status'] = 'resolved'; data['winner'] = 'u2'; negotiation.user2_koz -= 1
                        elif decision == 'yield': # Taviz Ver
                            if is_user1:
                                data['final'] = data['p2']; data['status'] = 'resolved'; data['winner'] = 'u2'; negotiation.user1_koz += 1
                            else:
                                data['final'] = data['p1']; data['status'] = 'resolved'; data['winner'] = 'u1'; negotiation.user2_koz += 1
                
                # Tüm maddeler çözüldüyse ACCEPTED, değilse turu devret
                if not any(v['status'] == 'pending' for v in conflicts.values()):
                    negotiation.status = 'ACCEPTED'
                else:
                    negotiation.current_turn = other_user
                
                negotiation.save()
                return redirect('negotiation_board', match_id=match_id)

    is_my_turn = (negotiation.current_turn == request.user)
    my_koz = negotiation.user1_koz if is_user1 else negotiation.user2_koz

    return render(request, 'core/negotiation_board.html', {
        'negotiation': negotiation, 'other_user': other_user,
        'conflicts': negotiation.current_offer, 'is_my_turn': is_my_turn,
        'my_koz': my_koz, 'is_user1': is_user1
    })

@login_required
def check_new_matches(request):
    # Kullanıcının aktif ve devam eden bir müzakeresi var mı kontrol et
    active_negotiation = Negotiation.objects.filter(
        match__user_1=request.user, status='ONGOING'
    ).first() or Negotiation.objects.filter(
        match__user_2=request.user, status='ONGOING'
    ).first()

    if active_negotiation:
        return JsonResponse({'has_new': True, 'match_id': active_negotiation.match.id})
    return JsonResponse({'has_new': False})

def active_match_ping(request):
    """Kullanıcının aktif bir masası varsa onu anında o URL'ye çeker."""
    if not request.user.is_authenticated:
        return JsonResponse({'active': False})
    
    active_neg = Negotiation.objects.filter(
        Q(match__user_1=request.user) | Q(match__user_2=request.user),
        status='ONGOING'
    ).first()
    
    if active_neg:
        return JsonResponse({'active': True, 'url': f'/negotiation/{active_neg.match.id}/'})
    return JsonResponse({'active': False})

@login_required
def negotiation_status_api(request, match_id):
    neg = Negotiation.objects.filter(match_id=match_id).first()
    if not neg:
        return JsonResponse({'status': 'DELETED'})
    
    is_user1 = (request.user == neg.match.user_1)
    # Sıra kimde, kim mühürledi, kriz çıktı mı? Hepsini gönderiyoruz.
    return JsonResponse({
        'status': neg.status,
        'current_turn_id': neg.current_turn.id if neg.current_turn else None,
        'opp_ready': neg.user2_ready if is_user1 else neg.user1_ready,
    })