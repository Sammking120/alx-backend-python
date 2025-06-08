from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import User, Conversation, Message

admin.site.register(User, UserAdmin)
admin.site.register(Conversation)
admin.site.register(Message)
