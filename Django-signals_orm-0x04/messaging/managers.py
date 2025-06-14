from django.db import models

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        """
        Return unread messages where the user is the receiver.
        Optimized with .only() for necessary fields.
        """
        return self.filter(receiver=user, is_read=False).only(
            'id', 'sender', 'receiver', 'content', 'timestamp', 'is_read'
        ).select_related('sender')