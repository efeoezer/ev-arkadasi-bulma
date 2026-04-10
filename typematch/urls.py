from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Uygulama Yolları
    path('', include('core.urls')),           # Ana sayfa ve eşleşme (core)
    path('accounts/', include('accounts.urls')), # Giriş/Kayıt (accounts)
    path('chat/', include('chat.urls')),         # Mesajlaşma (chat)

    # Şifre Sıfırlama (Django Standart)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='core/forgot_password.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
