from django.contrib import admin
from .models import MBTIType, Profile, LifestyleTag, UserLifestyle, Match

# Veritabanı tablolarının arayüze entegre edilmesi
admin.site.register(MBTIType)
admin.site.register(Profile)
admin.site.register(LifestyleTag)
admin.site.register(UserLifestyle)
admin.site.register(Match)
