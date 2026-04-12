from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True, help_text="Kullanıcının kendisini tanıttığı kısa biyografi.")
    city = models.CharField(max_length=100, blank=True, null=True, help_text="Yaşadığı şehir")
    mbti_type = models.CharField(max_length=4, blank=True, null=True)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    GENDER_CHOICES = [
        ('male', 'Erkek'),
        ('female', 'Kadın'),
        ('other', 'Diğer'),
        ('prefer_not_to_say', 'Belirtmek İstemiyorum')
    ]
    
    # Temel Kullanıcı Bağlantısı
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Kişisel ve Eğitim Bilgileri (Mevcut kodlarını buraya ekle)
    bio = models.TextField(max_length=500, blank=True, verbose_name="Hakkımda")
    # ... (Diğer alanların burada durmaya devam etsin)

    # AKTİFLİK TAKİBİ İÇİN GEREKLİ ALAN
    last_seen = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Son Görülme"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

    # AKTİFLİK KONTROLÜ FONKSİYONU
    def is_online(self):
        """Kullanıcının son 5 dakika içinde aktif olup olmadığını döner."""
        if self.last_seen:
            return timezone.now() < self.last_seen + datetime.timedelta(minutes=5)
        return False

    @property
    def age(self):
        if self.birth_date:
            return (datetime.date.today() - self.birth_date).days // 365
        return None
    
    def __str__(self):
        return f"{self.user.username} - {self.mbti_type if self.mbti_type else 'Belirsiz'}"

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


   

