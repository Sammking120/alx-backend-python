from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
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

@login_required
def delete_user(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            user.delete()  # Delete the user, triggering post_delete signal
            messages.success(request, "Your account has been deleted successfully.")
            return redirect('login')
        else:
            messages.error(request, "Incorrect password. Please try again.")
    return render(request, 'messaging/delete_user.html')