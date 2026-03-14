from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Core uygulamasının URL rotalarını ana sisteme (Root) bağlıyoruz
    path('', include('core.urls')), 
]
