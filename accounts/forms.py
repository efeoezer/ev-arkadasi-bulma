from django import forms
from django.contrib.auth.models import User
from .models import Profile, UserPhoto

# 1. Kullanıcı (User) tablosundaki temel bilgileri güncellemek için
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

# 2. Profil (Profile) tablosundaki ekstra bilgileri güncellemek için
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'city']

class PhotoUpdateForm(forms.ModelForm):
    class Meta:
        model = UserPhoto
        fields = ['image']
        labels = {
            'image': 'Profil Fotoğrafı Seç'
        }
