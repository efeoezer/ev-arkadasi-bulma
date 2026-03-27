from django.contrib import admin
from .models import Profile, RoommatePreference, Verification, Match, Like, Message, Review, UserPhoto

admin.site.register(Profile)
admin.site.register(RoommatePreference)
admin.site.register(Verification)
admin.site.register(Match)
admin.site.register(Like)
admin.site.register(Message)
admin.site.register(Review)
admin.site.register(UserPhoto)
