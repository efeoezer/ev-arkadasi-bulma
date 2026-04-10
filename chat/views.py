from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message

@login_required
def chat_view(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    
    # 1. Mesajları okundu olarak işaretle
    Message.objects.filter(sender=receiver, receiver=request.user, is_read=False).update(is_read=True)
    
    # 2. Mesaj gönderimi
    if request.method == "POST":
        content = request.POST.get('message_text') or request.POST.get('content') # İki ihtimali de ekledik
        if content:
            Message.objects.create(sender=request.user, receiver=receiver, content=content)
            return redirect('chat', receiver_id=receiver_id)

    # 3. Geçmiş mesajları getir
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('sent_at')

    return render(request, 'core/chat.html', { # Template hala core içindeyse yolu bozma
        'messages': messages,
        'receiver': receiver
    })