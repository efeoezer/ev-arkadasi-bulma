from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Gelen tüm istekleri doğrudan core uygulamasının urls.py dosyasına yönlendirir
    path('', include('core.urls')), 
    # Şifre Sıfırlama Yolları
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='core/forgot_password.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
