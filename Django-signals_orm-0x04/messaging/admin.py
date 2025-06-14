from django.contrib import admin
from .models import Message, Notification

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'content', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'content')
    date_hierarchy = 'timestamp'
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'receiver')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message__content')
    date_hierarchy = 'created_at'
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'message')