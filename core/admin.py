from django.contrib import admin
from .models import RoommatePreference, Match, Like, Review, Profile, Negotiation

admin.site.register(RoommatePreference)
admin.site.register(Match)
admin.site.register(Like)
admin.site.register(Review)
admin.site.register(Negotiation)
