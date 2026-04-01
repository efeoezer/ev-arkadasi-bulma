from django.contrib import admin
from .models import Profile, UserPhoto, Verification

admin.site.register(Profile)
admin.site.register(UserPhoto)
admin.site.register(Verification)
