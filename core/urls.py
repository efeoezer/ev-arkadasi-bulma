from django.urls import path
from . import views

urlpatterns = [
    # Ana Giriş Sayfası (Kayıt/Giriş butonu olan yer)
    path('', views.index_view, name='index'),

    # Ana Panel (Kartların olduğu yer)
    path('dashboard/', views.dashboard, name='dashboard'),

    # Eşleşmelerim Sayfası
    path('matches/', views.matches_view, name='matches'),

    # --- API ve Bot Araçları (Arka Plandaki İşlemler) ---

    # Kart Kaydırma API'si
    path('api/swipe/', views.swipe_api, name='swipe_api'),

    # Admin: Bot Üretme API'si
    path('api/generate-bots/', views.generate_bots_view, name='generate_bots'),

    # Admin: Test amaçlı botların kendine like atmasını sağlama
    path('api/bots-like-me/', views.make_bots_like_me, name='make_bots_like_me'),

    path('match-success/<int:match_with_id>/', views.match_success_view, name='match_success_view'),

    path('negotiation/<int:match_id>/', views.negotiation_board, name='negotiation_board'),

    path('delete-match/<int:match_id>/', views.delete_match, name='delete_match'),

    path('api/check-new-matches/', views.check_new_matches, name='check_new_matches'),

    path('api/active-match-ping/', views.active_match_ping, name='active_match_ping'),

    path('api/negotiation-status/<int:match_id>/', views.negotiation_status_api, name='negotiation_status_api')

]
