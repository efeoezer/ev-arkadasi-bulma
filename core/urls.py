from django.urls import path
from . import views

urlpatterns = [
    # Ana Sayfa (Giriş / Kayıt Ekranı)
    path('', views.index_view, name='index'),

    # Kontrol Paneli (Ana Ekran)
    path('dashboard/', views.dashboard, name='dashboard'),

    # Kosinüs Benzerliği Algoritması
    path('api/match/<int:user1_id>/<int:user2_id>/', views.calculate_match_api, name='api_match'),
    
    # Kimlik Doğrulama (Auth) Uç Noktaları
    path('api/register/', views.register_api, name='api_register'),
    path('api/login/', views.login_api, name='api_login'),
    path('api/logout/', views.logout_api, name='api_logout'),
]
