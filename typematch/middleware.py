from django.utils import timezone
from accounts.models import Profile

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Kullanıcı giriş yapmış mı kontrol et
        if request.user.is_authenticated:
            # 2. Kullanıcının profilini bul ve son görülme zamanını "şimdi" yap
            # update() kullanıyoruz çünkü daha hızlıdır ve save() sinyallerini tetiklemez
            Profile.objects.filter(user=request.user).update(last_seen=timezone.now())
        
        response = self.get_response(request)
        return response
