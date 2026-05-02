from django.contrib import admin
from .models import Profile, UserPhoto, Verification

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_seen', 'get_online_status')
    list_display = ['user', 'is_verified', 'is_online'] # Admin panelinde yan yana gösterilecek alanlar
    list_editable = ['is_verified']                    # Doğrudan listeden tik atıp kaydetmeyi sağlar
    list_filter = ['is_verified']                      # Sağ tarafa filtreleme menüsü ekler
    
    def get_online_status(self, obj):
        return obj.is_online()
    
    get_online_status.boolean = True
    get_online_status.short_description = "Aktif mi?"
    
admin.site.register(UserPhoto)
admin.site.register(Verification)

