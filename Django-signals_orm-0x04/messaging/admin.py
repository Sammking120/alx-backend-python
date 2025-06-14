from django.contrib import admin
from .models import Message, Notification, MessageHistory, DeletionLog

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'content', 'timestamp', 'is_read', 'edited', 'parent_message')
    list_filter = ('is_read', 'edited', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'content')
    date_hierarchy = 'timestamp'
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'receiver', 'parent_message')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message__content')
    date_hierarchy = 'created_at'
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'message')

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'old_content', 'edited_at', 'edited_by')
    list_filter = ('edited_at',)
    search_fields = ('message__content', 'old_content', 'edited_by__username')
    date_hierarchy = 'edited_at'
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('message', 'edited_by')

@admin.register(DeletionLog)
class DeletionLogAdmin(admin.ModelAdmin):
    list_display = ('username', 'deleted_at')
    list_filter = ('deleted_at',)
    date_hierarchy = 'deleted_at'
    list_per_page = 25