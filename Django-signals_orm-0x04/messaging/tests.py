from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from messaging.models import Message, Notification, MessageHistory
from django.core.cache import cache
import time

class MessageSignalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')
        cache.clear()  # Clear cache before each test

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
        parent_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message"
        )
        reply = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply message",
            parent_message=parent_message
        )
        nested_reply = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Nested reply",
            parent_message=reply
        )
        self.assertEqual(parent_message.replies.count(), 1, "Parent should have one direct reply") # type: ignore
        self.assertEqual(reply.replies.count(), 1, "Reply should have one nested reply") # type: ignore
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
        with self.assertNumQueries(2):
            messages = Message.objects.filter(sender=self.sender, parent_message__isnull=True)\
                .select_related('receiver').prefetch_related('replies')
            for message in messages:
                _ = message.receiver.username
                _ = [reply.content for reply in message.replies.all()] # type: ignore

    def test_unread_messages_manager(self):
        unread_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Unread message",
            is_read=False
        )
        read_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Read message",
            is_read=True
        )
        unread_messages = Message.unread.unread_for_user(self.receiver)
        self.assertEqual(unread_messages.count(), 1, "Should return only unread messages")
        self.assertIn(unread_message, unread_messages, "Unread message should be included")
        self.assertNotIn(read_message, unread_messages, "Read message should not be included")
        with self.assertNumQueries(1):
            for message in unread_messages:
                _ = message.content
                _ = message.sender.username

    def test_unread_messages_view(self):
        self.client.login(username='receiver', password='testpass')
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Unread message",
            is_read=False
        )
        response = self.client.get(reverse('messaging:message_list'))
        self.assertEqual(response.status_code, 200, "Should render message list")
        self.assertEqual(len(response.context['unread_messages']), 1, "Should show one unread message")
        unread_message = response.context['unread_messages'][0]
        self.assertEqual(unread_message.content, "Unread message")
        self.assertFalse(hasattr(unread_message, 'edited'), "Non-selected field should not be fetched")

    def test_message_list_cache(self):
        self.client.login(username='receiver', password='testpass')
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message",
            is_read=False
        )
        # First request: should hit the database
        with self.assertNumQueries(4):  # Queries for user, sent, received, unread messages
            response1 = self.client.get(reverse('messaging:message_list'))
        content1 = response1.content
        # Second request within 60 seconds: should hit cache
        with self.assertNumQueries(0):  # No database queries
            response2 = self.client.get(reverse('messaging:message_list'))
        content2 = response2.content
        self.assertEqual(content1, content2, "Cached response should match original")
        # Add a new message and check if cache prevents update
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="New message",
            is_read=False
        )
        response3 = self.client.get(reverse('messaging:message_list'))
        self.assertEqual(
            len(response3.context['unread_messages']), 1,
            "Cache should show old data until timeout"
        )
        # Wait for cache to expire
        time.sleep(61)
        response4 = self.client.get(reverse('messaging:message_list'))
        self.assertEqual(
            len(response4.context['unread_messages']), 2,
            "After cache expiry, new message should appear"
        )