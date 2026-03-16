from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Gelen tüm istekleri doğrudan core uygulamasının urls.py dosyasına yönlendirir
    path('', include('core.urls')), 
]
