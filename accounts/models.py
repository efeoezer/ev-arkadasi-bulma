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
    
    DIET_CHOICES = [
    ('omnivore', 'Hepçil (🥩)'),
    ('vegetarian', 'Vejetaryen (🥦)'),
    ('vegan', 'Vegan (🌱)'),
]
    # Pazarlık Masasında Kullanılacak Yaşam Tarzı Seçenekleri
    CLEANING_CHOICES = [
        ('DAILY', 'Her gün'),
        ('WEEKLY', 'Haftada bir'),
        ('BIWEEKLY', 'İki haftada bir'),
        ('RELAXED', 'Kirlendikçe'),
    ]

    GUEST_POLICY_CHOICES = [
        ('NO_GUESTS', 'Misafir kesinlikle yasak'),
        ('WEEKENDS', 'Sadece hafta sonları'),
        ('ANYTIME', 'Önceden haber vererek her zaman'),
    ]
    
    SLEEP_SCHEDULE_CHOICES = [
        ('EARLY_BIRD', 'Erkenci (Gece 12 öncesi sessizlik)'),
        ('NIGHT_OWL', 'Gece Kuşu (Gece ses sorun olmaz)'),
        ('FLEXIBLE', 'Esnek (Uyku saatim değişir)'),
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
    diet_preference = models.CharField(max_length=20, choices=DIET_CHOICES, default='omnivore', verbose_name="Diyet Tercihi")
    has_pet = models.BooleanField(default=False, verbose_name="Evcil Hayvanı Var")
    has_allergy = models.BooleanField(default=False, verbose_name="Alerjisi Var")

    # Pazarlık Parametreleri
    cleaning_frequency = models.CharField(max_length=20, choices=CLEANING_CHOICES, default='WEEKLY', verbose_name="Temizlik Sıklığı")
    guest_policy = models.CharField(max_length=20, choices=GUEST_POLICY_CHOICES, default='WEEKENDS', verbose_name="Misafir Politikası")
    sleep_schedule = models.CharField(max_length=20, choices=SLEEP_SCHEDULE_CHOICES, default='FLEXIBLE', verbose_name="Uyku Düzeni")
    smoking_allowed = models.BooleanField(default=False, verbose_name="Evde Sigara İçilebilir")
    pets_allowed = models.BooleanField(default=False, verbose_name="Evcil Hayvan Kabul Ediyor") # has_pet'ten farklıdır!
    # Güvenilir Kullanıcı Rozeti Alanı
    is_verified = models.BooleanField(default=False, help_text="Kullanıcının hesabı doğrulanmış mı?")
    
    # Sistem Takibi
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Son Görülme")
    created_at = models.DateTimeField(auto_now_add=True)
    is_onboarded = models.BooleanField(default=False)

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
        
    @property
    def display_name(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        return full_name if full_name else self.user.username

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
