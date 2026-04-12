from django import forms
from django.contrib.auth.models import User
from .models import Profile, UserPhoto

# 1. Kullanıcı Bilgileri
class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Adınız", 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Örn: Adınız'})
    )
    last_name = forms.CharField(
        label="Soyadınız", 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Örn: Soyadınız (Opsiyonel)'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

# 2. Profil Bilgileri 
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'city', 'country', 'mbti_type']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Kendinden biraz bahset...'}),
            'mbti_type': forms.Select(attrs={'class': 'custom-select'}),
        }

# 3. Fotoğraf Güncelleme
class PhotoUpdateForm(forms.ModelForm):
    class Meta:
        model = UserPhoto
        fields = ['image']
        labels = {'image': 'Profil Fotoğrafı Seç'}
