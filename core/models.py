from django.db import models
from django.contrib.auth.models import User

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
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    
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
