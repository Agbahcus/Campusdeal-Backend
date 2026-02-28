from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    # Chat Management
    path('', views.list_chats, name='list-chats'),
    path('create/', views.create_chat, name='create-chat'),
    path('<int:chat_id>/', views.get_chat, name='get-chat'),
    path('unread-count/', views.get_unread_count, name='unread-count'),
    
    # Messaging
    path('<int:chat_id>/messages/', views.get_messages, name='get-messages'),
    path('<int:chat_id>/messages/send/', views.send_message, name='send-message'),
    path('<int:chat_id>/mark-read/', views.mark_messages_read, name='mark-read'),
    
    # Moderation (Admin)
    path('moderation-logs/', views.get_moderation_logs, name='moderation-logs'),
    
    # Testing (Development Only)
    path('test-moderator/', views.test_moderator, name='test-moderator'),
]