from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.register_api, name='register_api'),
    path('api/login/', views.login_api, name='login_api'),
    path('api/logout/', views.logout_api, name='logout_api'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/delete-photo/', views.delete_photo_view, name='delete_photo'),
    path('profile/delete-account/', views.delete_account_view, name='delete_account'),
]
