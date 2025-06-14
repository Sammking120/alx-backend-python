from linecache import cache
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory, DeletionLog
from django.urls import reverse
from django.core.cache import cache
from django.db import models


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )
        # Invalidate message_list cache for receiver
        cache_key = f"views.decorators.cache.cache_page.{reverse('messaging:message_list')}.{instance.receiver.id}"
        cache.delete(cache_key)

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:  # Check if message already exists (i.e., it's an update)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Check if content changed
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender  # Assuming sender is the editor
                )
                instance.edited = True  # Mark message as edited
        except Message.DoesNotExist:
            pass  # Handle case where message doesn't exist yet
        
@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    DeletionLog.objects.create(username=instance.username)
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(edited_by=instance).delete()