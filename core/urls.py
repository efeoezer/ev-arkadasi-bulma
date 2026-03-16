from django.urls import path
from . import views

urlpatterns = [
    # Ana Sayfa (Frontend İskeleti)
    path('', views.index_view, name='index'),

    # Kosinüs Benzerliği Algoritması
    path('api/match/<int:user1_id>/<int:user2_id>/', views.calculate_match_api, name='api_match'),
    
    # Kimlik Doğrulama (Auth) Uç Noktaları
    path('api/register/', views.register_api, name='api_register'),
    path('api/login/', views.login_api, name='api_login'),
    path('api/logout/', views.logout_api, name='api_logout'),
]
from django.urls import path
from .views import *

urlpatterns = [
    path('', index_view),

    path('api/register/', register_api),
    path('api/login/', login_api),
    path('api/logout/', logout_api),

    path('api/match/<int:user1_id>/<int:user2_id>/', calculate_match_api),

]
