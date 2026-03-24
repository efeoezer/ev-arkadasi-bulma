from django.contrib import admin
from .models import Profile, LifestyleTag, UserLifestyle, Match

# Veritabanı tablolarının arayüze entegre edilmesi
admin.site.register(Profile)
admin.site.register(LifestyleTag)
admin.site.register(UserLifestyle)
admin.site.register(Match)
