"""
ASGI config for typematch project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'typematch.settings')

# HTTP isteklerini karşılaması için Django'nun standart ASGI uygulamasını başlatıyoruz
django_asgi_app = get_asgi_application()

# Kanalları (Channels) ve yönlendirmeleri dahil ediyoruz
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

application = ProtocolTypeRouter({
    # Normal web sayfaları için standart HTTP yönlendirmesi
    "http": django_asgi_app,
    
    # Anlık mesajlaşma için WebSocket yönlendirmesi
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})