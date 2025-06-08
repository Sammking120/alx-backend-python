from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Message, Conversation

class MessageFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    conversation = filters.NumberFilter(field_name='conversation__conversation_id')
    sender = filters.NumberFilter(field_name='sender__user_id')
    search = filters.CharFilter(method='search_messages')

    def search_messages(self, queryset, name, value):
        return queryset.filter(message_body__icontains=value)

    class Meta:
        model = Message
        fields = ['start_date', 'end_date', 'conversation', 'sender']

class ConversationFilter(filters.FilterSet):
    participant = filters.NumberFilter(method='filter_participant')
    
    def filter_participant(self, queryset, name, value):
        return queryset.filter(participants__user_id=value)

    class Meta:
        model = Conversation
        fields = ['participant']