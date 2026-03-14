from django.urls import path
from . import views

urlpatterns = [
    # Örnek kullanım: /api/match/1/2/ (1 ve 2 numaralı kullanıcıları eşleştirir)
    path('api/match/<int:user1_id>/<int:user2_id>/', views.calculate_match_api, name='api_match'),
]
