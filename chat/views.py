from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden
from core.models import Match
from .models import Conversation, Message
from core.services import get_icebreaker_prompts

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

    # 2. MİMARİ: SOHBET ODASINI (CONVERSATION) BUL VEYA YARAT
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=receiver).first()
    
    if not conversation:
        # Eğer daha önce hiç konuşmadıysanız, sıfırdan bir oda yarat
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, receiver)

    # 3. MESAJLARI OKUNDU YAP
    conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
    
    # 4. MESAJ GÖNDERME
    if request.method == "POST":
        content = request.POST.get('message_text', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation, 
                sender=request.user, 
                content=content
            )
            return redirect('chat', receiver_id=receiver_id)

    # 5. VERİ ÇEKME OPTİMİZASYONU: Odaya ait tüm mesajları çek
    messages = conversation.messages.select_related('sender').order_by('created_at')

    # Buzkıran soruları
    icebreakers = get_icebreaker_prompts(request.user.profile, receiver.profile)

    return render(request, 'core/chat.html', {
        'messages': messages,
        'receiver': receiver,
        'conversation': conversation,
        'icebreakers': icebreakers,
    })