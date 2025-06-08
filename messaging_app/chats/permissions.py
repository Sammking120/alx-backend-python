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