from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from .models import Message, MessageHistory
from django import forms

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your reply...'}),
        }

@login_required
def message_list(request):
    # Optimize queries with select_related and prefetch_related
    sent_messages = Message.objects.filter(sender=request.user, parent_message__isnull=True)\
        .select_related('receiver').prefetch_related('replies')
    received_messages = Message.objects.filter(receiver=request.user, parent_message__isnull=True)\
        .select_related('sender').prefetch_related('replies')
    return render(request, 'messaging/message_list.html', {
        'sent_messages': sent_messages,
        'received_messages': received_messages,
        'reply_form': ReplyForm()
    })

@login_required
def message_history(request, message_id):
    message = get_object_or_404(Message.objects.select_related('sender', 'receiver', 'parent_message'), id=message_id)
    if request.user not in [message.sender, message.receiver]:
        return render(request, 'messaging/error.html', {'error': 'You are not authorized to view this message.'}, status=403)
    history = MessageHistory.objects.filter(message=message).select_related('edited_by')
    threaded_replies = message.get_threaded_replies().select_related('sender', 'receiver', 'parent_message')
    return render(request, 'messaging/message_history.html', {
        'message': message,
        'history': history,
        'threaded_replies': threaded_replies,
        'reply_form': ReplyForm()
    })

@login_required
def reply_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if request.user not in [message.sender, message.receiver]:
        return render(request, 'messaging/error.html', {'error': 'You are not authorized to reply to this message.'}, status=403)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.receiver = message.sender if request.user == message.receiver else message.receiver
            reply.parent_message = message
            reply.save()
            messages.success(request, "Reply sent successfully.")
            return redirect('messaging:message_history', message_id=message.pk)
    return redirect('messaging:message_history', message_id=message.pk)

@login_required
def delete_user(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            user.delete()
            messages.success(request, "Your account has been deleted successfully.")
            return redirect('login')
        else:
            messages.error(request, "Incorrect password. Please try again.")
    return render(request, 'messaging/delete_user.html')