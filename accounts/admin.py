from django.contrib import admin
from .models import Profile, UserPhoto, Verification

# Diğer modelleri normal şekilde kaydet
admin.site.register(UserPhoto)
admin.site.register(Verification)

# Profile modelini ÖZEL ayarlarla kaydet
@admin.register(Profile) # Bu satır zaten kaydı yapar, yukarıdakine gerek kalmaz
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_seen', 'is_online_status') # İsim karışmaması için '_status' ekledik
    
    def is_online_status(self, obj):
        return obj.is_online()
    
    is_online_status.boolean = True  # Yeşil/Kırmızı ikon
    is_online_status.short_description = "Aktif mi?" # Sütun başlığı
