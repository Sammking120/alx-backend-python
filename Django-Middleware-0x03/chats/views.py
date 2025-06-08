from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from .filters import MessageFilter, ConversationFilter
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("Welcome to the Chat API!")

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]  # type: ignore
    filterset_class = ConversationFilter
    search_fields = ['participants__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    from django.db.models import QuerySet

    def get_queryset(self) -> 'QuerySet[Conversation]':
        """Return conversations where the authenticated user is a participant."""
        return Conversation.objects.filter(participants=self.request.user).distinct()

    @action(detail=False, methods=['post'])
    def start_conversation(self, request):
        """Start a new conversation with a single participant."""
        participant_id = request.data.get('participant_id')
        if not participant_id:
            return Response({'error': 'Participant ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if str(participant_id) == str(request.user.pk):
            return Response({'error': 'Cannot start a conversation with yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participant = User.objects.get(pk=participant_id)
        except User.DoesNotExist:
            return Response({'error': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        conversations = Conversation.objects.filter(participants=request.user).filter(participants=participant).distinct()
        if conversations.exists():
            serializer = self.get_serializer(conversations.first())
            return Response(serializer.data, status=status.HTTP_200_OK)

        conversation = Conversation.objects.create()
        conversation.participants.set([request.user, participant])
        conversation.save()
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    from typing import Any
    from django.db.models.query import QuerySet

    def get_queryset(self):
        conversation = self.get_conversation()
        if not conversation.participants.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied(
                detail="You do not have permission to access this conversation.",
                code="permission_denied"
            )
        return Message.objects.filter(conversation=conversation)

    def perform_create(self, serializer):
        conversation = self.get_conversation()
        if not conversation.participants.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied(
                detail="You do not have permission to send messages in this conversation.",
                code="HTTP_403_FORBIDDEN"
            )
        serializer.save(sender=self.request.user, conversation=conversation)

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance is None or instance.sender != self.request.user:
            raise PermissionDenied(
                detail="You can only edit your own messages.",
                code="HTTP_403_FORBIDDEN"
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.sender != self.request.user:
            raise PermissionDenied(
                detail="You can only delete your own messages.",
                code="HTTP_403_FORBIDDEN"
            )
        instance.delete()

    def get_conversation(self):
        try:
            return Conversation.objects.get(
                conversation_id=self.kwargs['conversation_pk']
            )
        except Conversation.DoesNotExist:
            raise ValidationError({"error": "Conversation not found"})