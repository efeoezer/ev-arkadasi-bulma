from django.db import models
from django.contrib.auth.models import User
from accounts.models import Profile

# EV ARKADAŞI TERCİHLERİ
class RoommatePreference(models.Model):
    ROOM_TYPE_CHOICES = [
        ('private', 'Private Room'),
        ('shared', 'Shared Room')
    ]
    
    DIET_CHOICES = [
        ('none', 'Belirtilmemiş'),
        ('omnivore', 'Hepçil (Her şeyi yer)'),
        ('vegetarian', 'Vejetaryen'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pesketaryen')
    ]

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='preferences')
    
    # Ev ve Oda Tercihleri
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='private')
    max_roommates = models.IntegerField(default=1)
    
    # Temizlik ve Düzen (1-5 Skalası)
    cleanliness_level = models.IntegerField(default=3)
    cleaning_frequency = models.IntegerField(default=1, help_text="Haftalık temizlik sıklığı")
    
    # Mutfak ve Beslenme
    cooks_often = models.BooleanField(default=False)
    dietary_preference = models.CharField(max_length=20, choices=DIET_CHOICES, default='none')
    
    # Evcil Hayvan
    has_pet = models.BooleanField(default=False)
    pet_tolerance = models.BooleanField(default=True, help_text="Evde evcil hayvan kabul ediyor mu?")
    allergic_to_pets = models.BooleanField(default=False)
    
    # Sosyal Yaşam ve Gürültü (1-5 Skalası)
    guest_frequency = models.IntegerField(default=2, help_text="Haftalık misafir sıklığı")
    party_tolerance = models.IntegerField(default=3)
    noise_tolerance = models.IntegerField(default=3)
    
    # Finans ve Meslek
    budget_flexibility = models.IntegerField(default=3)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.profile.user.username} Tercihleri"

# EŞLEŞME MOTORU TABLOSU
class Match(models.Model):
    user_1 = models.ForeignKey(User, related_name='matches_as_user1', on_delete=models.CASCADE)
    user_2 = models.ForeignKey(User, related_name='matches_as_user2', on_delete=models.CASCADE)
    algorithm_score = models.DecimalField(max_digits=5, decimal_places=2) 
    matched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_1', 'user_2')

    def __str__(self):
        return f"{self.user_1.username} & {self.user_2.username} - Skor: {self.algorithm_score}"

# ETKİLEŞİM TABLOLARI (Like, Review)
class Like(models.Model):
    from_user = models.ForeignKey(User, related_name="likes_sent", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="likes_received", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_reviews")
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews")
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

def profile_pic_path(instance, filename):
    # Görselleri 'profile_pics/user_id/filename' şeklinde düzenli saklamak için
    return f'profile_pics/{instance.user.id}/{filename}'

class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Erkek'),
        ('female', 'Kadın'),
        ('other', 'Diğer'),
        ('prefer_not_to_say', 'Belirtmek İstemiyorum')
    ]
    OCCUPATION_STATUS = [
        ('student', 'Öğrenci'),
        ('working', 'Çalışan'),
        ('student_working', 'Hem Okuyor Hem Çalışıyor'),
        ('unemployed', 'Şu an Çalışmıyor'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=OCCUPATION_STATUS, 
        default='student',
        verbose_name="Çalışma Durumu"

    # Temel Kullanıcı Bağlantısı
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Kişisel Bilgiler
    bio = models.TextField(max_length=500, blank=True, verbose_name="Hakkımda")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Doğum Tarihi")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='prefer_not_to_say')
    profile_picture = models.ImageField(upload_to=profile_pic_path, null=True, blank=True)
    
    # Eğitim Bilgileri
    university = models.CharField(max_length=255, blank=True, null=True, verbose_name="Üniversite")
    department = models.CharField(max_length=255, blank=True, null=True, verbose_name="Bölüm")
    is_student = models.BooleanField(default=True)
  
    # İş Bilgileri (Opsiyonel)
    job_title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Meslek / Unvan")
    company = models.CharField(max_length=100, blank=True, null=True, verbose_name="Çalıştığı Yer / Şirket")
    
    # Konum Bilgisi
    city = models.CharField(max_length=100, blank=True, verbose_name="Yaşadığı Şehir")
    district = models.CharField(max_length=100, blank=True, verbose_name="İlçe/Semt")

    # Güvenilirlik ve Doğrulama
    is_verified = models.BooleanField(default=False, help_text="E-posta veya kimlik doğrulaması yapıldı mı?")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Sosyal Medya Linkleri (Opsiyonel güven artırıcı)
    instagram_username = models.CharField(max_length=50, blank=True, null=True)
    
    # Sistem Takibi
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

    @property
    def age(self):
        if self.birth_date:
            import datetime
            return (datetime.date.today() - self.birth_date).days // 365
        return None

    def is_online(self):
        if self.last_seen:
            now = timezone.now()
            return now < self.last_seen + timezone.timedelta(minutes=5)
        return False
