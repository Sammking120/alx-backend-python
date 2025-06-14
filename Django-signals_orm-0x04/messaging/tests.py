from django.test import TestCase
from django.contrib.auth.models import User
from messaging.models import Message, Notification

class MessageSignalTests(TestCase):
    def setUp(self):
        # Create test users
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')

    def test_notification_created_on_message_save(self):
        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )

        # Check if a notification was created for the receiver
        notification_exists = Notification.objects.filter(
            user=self.receiver,
            message=message
        ).exists()
        self.assertTrue(notification_exists, "Notification should be created for receiver")

        # Verify notification details
        notification = Notification.objects.get(user=self.receiver, message=message)
        self.assertFalse(notification.is_read, "Notification should be unread by default")
        self.assertEqual(notification.user, self.receiver, "Notification should be for the receiver")

    def test_no_notification_on_message_update(self):
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message"
        )

        # Count initial notifications
        initial_count = Notification.objects.count()

        # Update the message
        message.content = "Updated message"
        message.save()

        # Check that no new notification was created
        self.assertEqual(
            Notification.objects.count(),
            initial_count,
            "No new notification should be created on message update"
        )