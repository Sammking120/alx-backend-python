from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse, include
from messaging.models import Message, Notification, MessageHistory

class MessageSignalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')

    def test_notification_created_on_message_save(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        notification_exists = Notification.objects.filter(
            user=self.receiver,
            message=message
        ).exists()
        self.assertTrue(notification_exists, "Notification should be created for receiver")
        notification = Notification.objects.get(user=self.receiver, message=message)
        self.assertFalse(notification.is_read, "Notification should be unread by default")
        self.assertEqual(notification.user, self.receiver, "Notification should be for the receiver")

    def test_no_notification_on_message_update(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message"
        )
        initial_count = Notification.objects.count()
        message.content = "Updated message"
        message.save()
        self.assertEqual(
            Notification.objects.count(),
            initial_count,
            "No new notification should be created on message update"
        )

    def test_message_history_on_edit(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message"
        )
        original_content = message.content
        message.content = "Edited message"
        message.save()
        history_exists = MessageHistory.objects.filter(message=message).exists()
        self.assertTrue(history_exists, "Message history should be created on edit")
        history = MessageHistory.objects.get(message=message)
        self.assertEqual(history.old_content, original_content, "History should store original content")
        self.assertEqual(history.edited_by, self.sender, "History should record editor")
        self.assertTrue(message.edited, "Message should be marked as edited")

    def test_user_data_cleanup_on_delete(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        Notification.objects.create(user=self.receiver, message=message)
        MessageHistory.objects.create(message=message, old_content="Old content", edited_by=self.sender)
        self.sender.delete()
        self.assertFalse(Message.objects.filter(sender=self.sender).exists(), "Sender messages should be deleted")
        self.assertFalse(Message.objects.filter(receiver=self.sender).exists(), "Receiver messages should be deleted")
        self.assertFalse(Notification.objects.filter(user=self.sender).exists(), "Notifications should be deleted")
        self.assertFalse(MessageHistory.objects.filter(edited_by=self.sender).exists(), "Message history should be deleted")

    def test_delete_user_view(self):
        self.client.login(username='sender', password='testpass')
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        response = self.client.post(reverse('messaging:delete_user'), {'password': 'testpass'})
        self.assertEqual(response.status_code, 302, "Should redirect after deletion")
        self.assertFalse(User.objects.filter(username='sender').exists(), "User should be deleted")
        self.assertFalse(Message.objects.filter(sender=self.sender).exists(), "Messages should be deleted")

    def test_threaded_conversation(self):
        # Create a parent message
        parent_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message"
        )
        # Create a reply
        reply = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply message",
            parent_message=parent_message
        )
        # Create a nested reply
        nested_reply = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Nested reply",
            parent_message=reply
        )

        # Test reply relationships
        self.assertEqual(parent_message.replies.count(), 1, "Parent should have one direct reply") # type: ignore
        self.assertEqual(reply.replies.count(), 1, "Reply should have one nested reply") # type: ignore

        # Test recursive fetching
        threaded_replies = parent_message.get_threaded_replies()
        self.assertEqual(threaded_replies.count(), 2, "Should fetch both replies")
        self.assertIn(reply, threaded_replies, "Reply should be in threaded replies")
        self.assertIn(nested_reply, threaded_replies, "Nested reply should be in threaded replies")

    def test_query_optimization(self):
        parent_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message"
        )
        Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply message",
            parent_message=parent_message
        )

        with self.assertNumQueries(2):  # One for messages, one for replies
            messages = Message.objects.filter(sender=self.sender, parent_message__isnull=True)\
                .select_related('receiver').prefetch_related('replies')
            for message in messages:
                _ = message.receiver.username  # Access related field
                _ = [reply.content for reply in message.replies.all()]  # type: ignore # Access prefetched replies