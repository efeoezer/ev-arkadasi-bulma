from django.urls import path
from . import views

urlpatterns = [
    # Ana Sayfa (Giriş / Kayıt Ekranı)
    path('', views.index_view, name='index'),

    # Kontrol Paneli (Ana Ekran)
    path('dashboard/', views.dashboard, name='dashboard'),

    # Kosinüs Benzerliği Algoritması
    path('api/match/<int:user1_id>/<int:user2_id>/', views.calculate_match_api, name='api_match'),

    path('api/save_mbti/', views.save_mbti_api, name='api_save_mbti'),
    
    # MBTI Test Sayfası
    path('test/mbti/', views.mbti_test_view, name='mbti_test'),

    # Eşleşme Skoru Test API'si
    path('api/match/<int:user1_id>/<int:user2_id>/', views.calculate_match_api, name='api_match'),

    path('generate-bots/', views.generate_bots_view, name='generate_bots'),

    path('api/swipe/', views.swipe_api, name='swipe_api'),

    path('matches/', views.matches_view, name='matches'),

    path('api/bots-like-me/', views.make_bots_like_me, name='make_bots_like_me'),
]

urlpatterns = [
    # ... diğer adreslerin ...
    path('chat/<int:receiver_id>/', views.chat_view, name='chat'),
]
