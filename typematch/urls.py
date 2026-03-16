from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/match/<int:user1_id>/<int:user2_id>/', views.calculate_match_api),
    
    # Kimlik Doğrulama Uç Noktaları
    path('api/register/', views.register_api),
    path('api/login/', views.login_api),
    path('api/logout/', views.logout_api),
]
