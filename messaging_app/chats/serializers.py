from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """Create a new User instance with a hashed password."""
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_email(self, value):
        if "spam" in value:
            raise serializers.ValidationError("Invalid email address.")
        return value

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(read_only=True)
    message_body = serializers.CharField(required=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sender', 'conversation', 'sent_at']

    def create(self, validated_data):
        """Create a new message."""
        return Message.objects.create(**validated_data)

    def to_representation(self, instance):
        """Customize the message representation."""
        data = super().to_representation(instance)
        data['sender_name'] = instance.sender.get_full_name()
        return data

class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants',
                  'created_at', 'messages', 'message_count']
        read_only_fields = ['created_at']

    def get_message_count(self, obj):
        return obj.messages.count()