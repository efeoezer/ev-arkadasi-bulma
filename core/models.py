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

    # Misafir sıklığını % cinsine çevirir (Örn: 3 -> %60)
    @property
    def guest_frequency_percent(self):
        # 1-5 skalasını yüzdeye vurmak için: (değer / 5) * 100
        return min(max(int((self.guest_frequency / 5) * 100), 0), 100)

    # Gürültü toleransını % cinsine çevirir (Örn: 4 -> %80)
    @property
    def noise_tolerance_percent(self):
        return min(max(int((self.noise_tolerance / 5) * 100), 0), 100)
        
        

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
    STATUS_CHOICES = [
        ('ONGOING', 'Pazarlık Devam Ediyor'),
        ('ACCEPTED', 'Sözleşme İmzalandı'),
        ('REJECTED', 'Masa Devrildi'),
    ]

    # İlişkiyi 'Match' string'i yerine doğrudan Match modelini import ederek de verebilirsin
    match = models.OneToOneField('Match', on_delete=models.CASCADE, related_name='negotiation_board')
    
    # --- SATRANÇ MOTORU (State Machine) ---
    # Hamle sırasının kimde olduğunu takip eder. (P1 hamle yapınca buraya P2'nin ID'si yazılır)
    current_turn = models.ForeignKey(User, related_name='active_turns', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Müzakere sonsuza uzamasın diye tur sayacı
    round_number = models.IntegerField(default=1)
    
    # Masanın genel durumu
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ONGOING')
    
    # --- MASADAKİ SÖZLEŞME (Orta Yol) ---
    # İki ayrı user choice yerine, ortada DÖNEN TEK BİR TEKLİF var.
    # JSON içinde {'rent': 12000, 'cleaning': 'WEEKLY', ...} şeklinde güncel taslak tutulacak.
    current_offer = models.JSONField(default=dict, blank=True, verbose_name="Masadaki Güncel Teklif")
    
    # İyi niyet (Taviz) puanları - Sevdiğimiz bir mekanik olduğu için koruduk!
    # Sistem, profilinden en çok taviz verene bu puanı ekleyecek.
    user1_goodwill = models.IntegerField(default=0)
    user2_goodwill = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user1_ready = models.BooleanField(default=False)
    user2_ready = models.BooleanField(default=False)

    user1_choices = models.JSONField(default=dict, blank=True)
    user2_choices = models.JSONField(default=dict, blank=True)

    user1_koz = models.IntegerField(default=2)
    user2_koz = models.IntegerField(default=2)

    def __str__(self):
        return f"Müzakere Masası ID: {self.match.id} - Durum: {self.get_status_display()}"
