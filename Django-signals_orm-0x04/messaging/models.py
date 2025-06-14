from django.db import models
from django.contrib.auth.models import User
from .managers import UnreadMessagesManager

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE,
        help_text="The message this is a reply to, if any."
    )

    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['receiver', 'is_read']),
        ]

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

    def get_threaded_replies(self):
        """
        Recursively fetch all replies to this message, including nested replies.
        Returns a queryset with replies ordered by timestamp.
        """
        def collect_replies(message, replies_set):
            direct_replies = message.replies.all()
            for reply in direct_replies:
                replies_set.add(reply)
                collect_replies(reply, replies_set)

        replies_set = set()
        collect_replies(self, replies_set)
        return Message.objects.filter(id__in=[reply.id for reply in replies_set]).order_by('timestamp')

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user} about message {self.message.id}"

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-edited_at']

    def __str__(self):
        return f"Edit history for message {self.message.id} at {self.edited_at}"

class DeletionLog(models.Model):
    username = models.CharField(max_length=150)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.username} deleted at {self.deleted_at}"