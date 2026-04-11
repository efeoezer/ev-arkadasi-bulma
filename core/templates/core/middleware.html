from django.utils import timezone
from .models import Profile

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Eğer kullanıcı giriş yapmışsa last_seen alanını güncelle
        if request.user.is_authenticated:
            # .update() kullanmak sinyalleri (signals) tetiklemez ve daha performanslıdır
            Profile.objects.filter(user=request.user).update(last_seen=timezone.now())
        
        response = self.get_response(request)
        return response
        
