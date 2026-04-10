from django.urls import path
from . import views

urlpatterns = [
    # 1. Ana Giriş Sayfası (Kayıt/Giriş butonu olan yer)
    path('', views.index_view, name='index'),

    # 2. Ana Panel (Kartların olduğu yer)
    path('dashboard/', views.dashboard, name='dashboard'),

    # 3. MBTI Testi Sayfası
    path('mbti-test/', views.mbti_test_view, name='mbti_test'),

    # 4. Eşleşmelerim Sayfası
    path('matches/', views.matches_view, name='matches'),

    # --- API ve Bot Araçları (Arka Plandaki İşlemler) ---

    # Kart Kaydırma API'si
    path('api/swipe/', views.swipe_api, name='swipe_api'),

    # Admin: Bot Üretme API'si
    path('api/generate-bots/', views.generate_bots_view, name='generate_bots'),

    # Admin: Test amaçlı botların kendine like atmasını sağlama
    path('api/bots-like-me/', views.make_bots_like_me, name='make_bots_like_me'),
]