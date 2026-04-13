from django.contrib import admin
from .models import Profile, UserPhoto, Verification

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_seen', 'get_online_status')
    
    def get_online_status(self, obj):
        return obj.is_online()
    
    get_online_status.boolean = True
    get_online_status.short_description = "Aktif mi?"
    
admin.site.register(UserPhoto)
admin.site.register(Verification)

