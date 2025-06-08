from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid 

 
# Create your models here.
class Users(AbstractUser):
    '''Model representing a chat in the messaging app.'''
    email = models.CharField(max_length=255, unique=True)
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    primary_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password = models.CharField(max_length=255, unique=True)
    

    def __str__(self):
        return self.username
    

class Conversation (models.Model):
    '''model representing a conversation in the messaging app.'''
    conversation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    participants = models.ManyToManyField(Users, related_name='participants')


    def __str__(self):
        return f"Conversation between {self.participants.all()} with ID {self.conversation_id}"


class Message(models.Model):
    '''model representing a message in the messaging app.'''
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_messages')
    message_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    message_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message_id} sent at {self.sent_at} with body: {self.message_body}"