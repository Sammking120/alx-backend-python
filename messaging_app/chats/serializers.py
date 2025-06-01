from rest_framework import serializers
from .models import Users, Message, Conversation

class UsersSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, required=False)
    last_name = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = Users
        fields = ['name_of_user','Email_of_user','password','is_online']

class MessageSerializer(serializers.ModelSerializer):
    sender = UsersSerializer(read_only=True)
    message_id = serializers.UUIDField(read_only=True)
    message_body = serializers.CharField(max_length=500)
    timestamp = serializers.DateTimeField(read_only=True)
    message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['sender', 'message_id', 'message_body', 'timestamp', 'message_preview']

def validate_message(self , value):
    if not value.stip():
     raise serializers.ValidationError('message body cannot be empty')
    return value
        


class ConversationSerializer(serializers.ModelSerializer):
    participants = UsersSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True, source='messages')

    class Meta:
        model = Message
        fields = ['sender','conversation','text','timestamp','is_read','is_deleted']