from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, Conversation, Message
import json

class MessagingAPITests(APITestCase):
    def setUp(self):
        """Create test users and get tokens"""
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        
        # Get authentication token for user1
        response = self.client.post('/api/token/', {
            'email': 'user1@test.com',  # Changed from username to email
            'password': 'testpass123'
        }, format='json')
        
        # Debug response
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.content}")
        
        if response.status_code != 200:
            print(f"Error Response: {response.content}")
            raise Exception("Failed to obtain token")
        
        response_json = json.loads(response.content.decode('utf-8'))
        self.token = response_json['access']
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'

    def test_start_conversation(self):
        """Test starting a new conversation"""
        url = reverse('conversation-start-conversation')
        data = {'participant_id': self.user2.pk}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)
        
        # Verify conversation participants
        conversation = Conversation.objects.first()
        self.assertIsNotNone(conversation, "No conversation was created.")
        if conversation is not None:
            self.assertIn(self.user1, conversation.participants.all())
            self.assertIn(self.user2, conversation.participants.all())

    def test_send_message(self):
        """Test sending a message in a conversation"""
        # First create a conversation
        conversation = Conversation.objects.create()
        conversation.participants.set([self.user1, self.user2])
        
        url = reverse('message-list')
        data = {
            'conversation_id': conversation.pk,
            'message_body': 'Hello, this is a test message!'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()
        self.assertIsNotNone(message, "Message was not created.")
        if message is not None:
            self.assertEqual(message.message_body, 'Hello, this is a test message!')

    def test_unauthorized_access(self):
        """Test unauthorized access to conversations"""
        # Remove authentication
        if 'HTTP_AUTHORIZATION' in self.client.defaults:
            del self.client.defaults['HTTP_AUTHORIZATION']
        
        url = reverse('conversation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_conversation_list_filtering(self):
        """Test conversation listing and filtering"""
        # Create test conversations
        conversation1 = Conversation.objects.create()
        conversation1.participants.set([self.user1, self.user2])
        
        url = reverse('conversation-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_message_pagination(self):
        """Test message pagination"""
        # Create a conversation
        conversation = Conversation.objects.create()
        conversation.participants.set([self.user1, self.user2])
        
        # Create 25 test messages
        for i in range(25):
            Message.objects.create(
                sender=self.user1,
                conversation=conversation,
                message_body=f'Test message {i}'
            )
            
        url = reverse('message-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(len(response_json['results']), 20)  # Default pagination
        self.assertIsNotNone(response_json['next'])  # Should have next page

    def test_invalid_conversation_access(self):
        """Test accessing invalid conversation"""
        url = reverse('message-list')
        data = {
            'conversation_id': 999,  # Non-existent conversation
            'message_body': 'This should fail'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)