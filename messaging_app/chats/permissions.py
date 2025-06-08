from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View
from django.core.exceptions import PermissionDenied
from typing import Literal
from .models import Conversation, Message

class IsMessageSender(BasePermission):
    """
    Allows access only to the sender of the message.
    """
    def has_object_permission(self, request: Request, view: View, obj: Message) -> Literal[True]:
        if obj.sender != request.user:
            raise PermissionDenied("You are not the sender of this message.")
        return True

class IsConversationParticipant(BasePermission):
    """
    Allows access only to participants of the conversation.
    """
    def has_object_permission(self, request: Request, view: View, obj: Conversation) -> Literal[True]:
        if request.user not in obj.participants.all():
            raise PermissionDenied("You are not a participant in this conversation.")
        return True
    
class IsParticipantOfConversation(BasePermission):
    """
    Allows access only to authenticated users who are participants in the conversation.
    For Message objects, checks the associated conversation's participants.
    For Conversation objects, checks the participants directly.
    """
    def has_permission(self, request: Request, view: View) -> Literal[True]:
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")
        return True

    def has_object_permission(self, request: Request, view: View, obj: Conversation | Message) -> Literal[True]:
        # Handle Message objects
        if isinstance(obj, Message):
            conversation = obj.conversation
        # Handle Conversation objects
        else:
            conversation = obj
        
        if not conversation.participants.filter(pk=request.user.pk).exists():
            raise PermissionDenied("You are not a participant in this conversation.")
        return True