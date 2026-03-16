from django.db import models
from django.contrib.auth.models import User

# Konum
class Location(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}, {self.country}"


# 1. REFERANS TABLOSU: MBTI Tipleri
class MBTIType(models.Model):
    type_code = models.CharField(max_length=4, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.type_code

# 2. PROFİL TABLOSU: Kullanıcıların detaylı verileri
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    mbti_type = models.ForeignKey(MBTIType, on_delete=models.SET_NULL, null=True)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.user.username

# 3. YAŞAM TARZI ETİKETLERİ: Temizlik, sigara, evcil hayvan vb.
class LifestyleTag(models.Model):
    category = models.CharField(max_length=50)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.category} - {self.name}"

# 4. KÖPRÜ TABLO (Junction Table): Hangi kullanıcının hangi etikete ne kadar önem verdiği
class UserLifestyle(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tag = models.ForeignKey(LifestyleTag, on_delete=models.CASCADE)
    weight = models.IntegerField(default=3) # 1 ile 5 arası önem derecesi (Algoritma için)

    def __str__(self):
        return f"{self.profile.user.username} -> {self.tag.name} (Ağırlık: {self.weight})"

# 5. EŞLEŞME MOTORU TABLOSU: Algoritmanın ürettiği sonuçlar
class Match(models.Model):
    user_1 = models.ForeignKey(User, related_name='matches_as_user1', on_delete=models.CASCADE)
    user_2 = models.ForeignKey(User, related_name='matches_as_user2', on_delete=models.CASCADE)
    algorithm_score = models.DecimalField(max_digits=5, decimal_places=2) # Örn: %85.50 uyum
    matched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_1.username} & {self.user_2.username} - Skor: {self.algorithm_score}"

#6. Ev tercihleri
class HousingPreference(models.Model):

    ROOM_TYPE_CHOICES = [
        ('private', 'Private Room'),
        ('shared', 'Shared Room')
    ]
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    max_roommates = models.IntegerField()
    has_pet = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.profile.user.username} Housing Preference"

#7. Profil için fotoğraf kısmı
class UserPhoto(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profile_photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.user.username} Photo"

#8. Kullanıcıların birbirlerini beğenmesi:
class Like(models.Model):
    from_user = models.ForeignKey(User, related_name="likes_sent", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="likes_received", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.username} likes {self.to_user.username}"

#9. Mesajlaşma sistemi
class Message(models.Model):

    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"

#10. Compability Score Tablosu(daha çok şey eklenebilir)
class CompatibilityScore(models.Model):

    user1 = models.ForeignKey(User, related_name="compatibility_user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="compatibility_user2", on_delete=models.CASCADE)
    mbti_score = models.FloatField()
    lifestyle_score = models.FloatField()
    interest_score = models.FloatField()
    total_score = models.FloatField()
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username} -> {self.total_score}"

# 11. Extrovert ya da introvert olup olmadığını ölçer
class PersonalityEorI(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    introvert_level = models.IntegerField()   # 1-5
    social_level = models.IntegerField()      # 1-5
    conflict_style = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.profile.user.username} PersonalityEorI"

#12. Ev kuralları uyumluluğu ölçer.
class HouseRules(models.Model):

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    guest_frequency = models.IntegerField()  # haftada kaç kez
    party_tolerance = models.IntegerField()  # 1-5
    quiet_hours_start = models.TimeField()
    quiet_hours_end = models.TimeField()

#13. Temizlik alışkanlığı uyumluluğu.
class CleaningHabit(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    cleanliness_level = models.IntegerField() # 1-5
    dishes_immediately = models.BooleanField()
    cleaning_frequency = models.IntegerField() # haftada kaç kez

#14. Evcil hayvan uyumlulığu:
class PetPreference(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    likes_dogs = models.BooleanField()
    likes_cats = models.BooleanField()
    allergic_to_pets = models.BooleanField()

#15. Mutfak kullanımı - uyumluluğu:
class KitchenHabit(models.Model):

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    cooks_often = models.BooleanField()
    shares_food = models.BooleanField()
    vegetarian = models.BooleanField()
    vegan = models.BooleanField()
    pescatarian = models.BooleanField()
    omnivor = models.BooleanField()

#16. Eğitim/Meslek saatlerinin uyumluluğu
class Occupation(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=100)
    university = models.CharField(max_length=100)
    working_hours = models.CharField(max_length=100)

#17 Finansal / Bütçe uyumluluğu
class FinancialHabit(models.Model):

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    pays_bills_on_time = models.BooleanField()
    budget_flexibility = models.IntegerField()  # 1-5

# 18. Gürültü tolerans seviyesi
class NoisePreference(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    music_volume = models.IntegerField()  # 1-5
    tolerance_to_noise = models.IntegerField()  # 1-5

#GÜVENLİK DOĞRULAMA SİSTEMİ!
class Verification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_verified = models.BooleanField(default=False)
    id_verified = models.BooleanField(default=False)

#KULLANICI DEĞERLENDİRME SİSTEMİ
class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_reviews")
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews")
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# 19. sabıka kaydı sorgulama.
class CriminalRecord(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    criminalrecord = models.OneToOneField(Profile, on_delete=models.CASCADE)
    
