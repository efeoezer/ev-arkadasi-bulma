from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True, help_text="Kullanıcının kendisini tanıttığı kısa biyografi.")
    city = models.CharField(max_length=100, blank=True, null=True, help_text="Yaşadığı şehir")
    mbti_type = models.CharField(max_length=4, blank=True, null=True)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.mbti_type if self.mbti_type else 'Belirsiz'}"
