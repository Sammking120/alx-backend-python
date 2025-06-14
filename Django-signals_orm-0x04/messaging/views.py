from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message, MessageHistory

@login_required
def message_list(request):
    sent_messages = Message.objects.filter(sender=request.user).select_related('receiver')
    received_messages = Message.objects.filter(receiver=request.user).select_related('sender')
    return render(request, 'messaging/message_list.html', {
        'sent_messages': sent_messages,
        'received_messages': received_messages
    })

@login_required
def message_history(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    # Ensure user is either sender or receiver
    if request.user not in [message.sender, message.receiver]:
        return render(request, 'messaging/error.html', {'error': 'You are not authorized to view this message.'}, status=403)
    history = MessageHistory.objects.filter(message=message).select_related('edited_by')
    return render(request, 'messaging/message_history.html', {
        'message': message,
        'history': history
    })