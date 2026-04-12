from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Erkek'),
        ('female', 'Kadın'),
        ('other', 'Diğer'),
        ('prefer_not_to_say', 'Belirtmek İstemiyorum')
    ]
    
    # Temel Bağlantı
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Kişisel Bilgiler
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="Hakkımda")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Doğum Tarihi")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='prefer_not_to_say', verbose_name="Cinsiyet")
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Yaşadığı Şehir")
    mbti_type = models.CharField(max_length=4, blank=True, null=True, verbose_name="MBTI Tipi")
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Bütçe Limiti")
    
    # Sistem Takibi
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Son Görülme")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mbti_type if self.mbti_type else 'Profil'}"

    def is_online(self):
        """Kullanıcının son 5 dakika içinde aktif olup olmadığını döner."""
        if self.last_seen:
            return timezone.now() < self.last_seen + timezone.timedelta(minutes=5)
        return False

    @property
    def age(self):
        if hasattr(self, 'birth_date') and self.birth_date:
            import datetime
            return (datetime.date.today() - self.birth_date).days // 365
        return None

class UserPhoto(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profile_photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Verification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_verified = models.BooleanField(default=False)
    id_verified = models.BooleanField(default=False)
    has_criminal_record = models.BooleanField(default=False, help_text="Resmi sabıka kaydı beyanı")

    def __str__(self):
        return f"{self.user.username} Doğrulama Durumu"
