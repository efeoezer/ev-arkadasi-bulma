from django.contrib import admin
from .models import Profile, UserPhoto, Verification

# Diğer modelleri sade bir şekilde kaydet
admin.site.register(UserPhoto)
admin.site.register(Verification)

# Profile modelini özel ayarlar (sütunlar) ile kaydet
class ProfileAdmin(admin.ModelAdmin):
    # Panel listesinde görünecek sütunlar
    list_display = ('user', 'last_seen', 'online_status')
    
    # Sıralama: En son aktif olan en üstte gözüksün
    ordering = ('-last_seen',)

    def online_status(self, obj):
        return obj.is_online()
    
    online_status.boolean = True  # Yeşil tik / Kırmızı çarpı ikonu
    online_status.short_description = "Aktif mi?" # Sütun başlığı

# En önemli satır: Modeli ve yukarıdaki ayarları birbirine bağla
admin.site.register(Profile, ProfileAdmin)
