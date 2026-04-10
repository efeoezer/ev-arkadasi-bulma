from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden
from core.models import Match # Eşleşme kontrolü için
from .models import Message

@login_required
def chat_view(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    
    # 1. GÜVENLİK: Bu iki kullanıcı gerçekten eşleşmiş mi?
    is_matched = Match.objects.filter(
        (Q(user_1=request.user) & Q(user_2=receiver)) |
        (Q(user_1=receiver) & Q(user_2=request.user))
    ).exists()
    
    if not is_matched:
        return HttpResponseForbidden("Sadece eşleştiğiniz kişilerle mesajlaşabilirsiniz.")

    # 2. MESAJLARI OKUNDU YAP (Sadece bana gelenleri)
    Message.objects.filter(
        sender=receiver, 
        receiver=request.user, 
        is_read=False
    ).update(is_read=True)
    
    # 3. MESAJ GÖNDERME (Hataları ayıklanmış versiyon)
    if request.method == "POST":
        content = request.POST.get('message_text', '').strip()
        if content:
            Message.objects.create(
                sender=request.user, 
                receiver=receiver, 
                content=content
            )
            return redirect('chat', receiver_id=receiver_id)

    # 4. VERİ ÇEKME OPTİMİZASYONU: select_related ekledik
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).select_related('sender').order_by('sent_at')

    return render(request, 'core/chat.html', {
        'messages': messages,
        'receiver': receiver
    })
