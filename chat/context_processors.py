from .models import Message

def unread_badge(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return {'global_unread_count': count}
    return {'global_unread_count': 0}