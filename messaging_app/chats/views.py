from django.shortcuts import render
from django.db.models.query import QuerySet
from .models import Message, Conversation
from django.db.models.query import QuerySet
from typing import Any

# Create your views here.
from rest_framework import viewsets ,status , filters
from .models import Users, Message , Conversation
from .serializers import MessageSerializer, ConversationSerializer
from rest_framework.permissions import IsAuthenticated


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = [IsAuthenticated]
    search_fields = ['message_body']
    
   


# Create your views here.
class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants_username']

