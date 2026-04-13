from django.db import models
from django.contrib.auth.models import User
from accounts.models import Profile
from django.db.models import JSONField

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

class Negotiation(models.Model):
    match = models.OneToOneField('Match', on_delete=models.CASCADE, related_name='negotiation_board')
    
    # Kullanıcıların seçimleri JSON olarak tutulacak
    user1_choices = JSONField(default=dict, blank=True)
    user2_choices = JSONField(default=dict, blank=True)
    
    # Seçimler kilitlendi mi?
    user1_ready = models.BooleanField(default=False)
    user2_ready = models.BooleanField(default=False)
    
    # İyi niyet (Taviz) puanları
    user1_goodwill = models.IntegerField(default=0)
    user2_goodwill = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Müzakere Masası ID: {self.match.id}"
