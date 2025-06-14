from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.message_list, name='message_list'),
    path('history/<int:message_id>/', views.message_history, name='message_history'),
    path('reply/<int:message_id>/', views.reply_message, name='reply_message'),
    path('delete/', views.delete_user, name='delete_user'),
]