from django.contrib import admin
from .models import Chat, Message, ModeratedMessageLog


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'participant_1',
        'participant_2',
        'related_item',
        'last_message_time',
        'created_at'
    ]
    list_filter = ['created_at', 'last_message_time']
    search_fields = [
        'participant_1__username',
        'participant_2__username',
        'related_item__title'
    ]
    readonly_fields = ['created_at', 'last_message_time']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'chat',
        'sender',
        'text_preview',
        'is_flagged',
        'is_system_warning',
        'created_at'
    ]
    list_filter = [
        'is_flagged',
        'is_system_warning',
        'is_deleted_by_system',
        'created_at'
    ]
    search_fields = ['sender__username', 'text']
    readonly_fields = ['created_at']
    
    def text_preview(self, obj):
        """Show first 50 characters of message"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Message'


@admin.register(ModeratedMessageLog)
class ModeratedMessageLogAdmin(admin.ModelAdmin):
    list_display = [
        'original_sender',
        'strike_number',
        'action_taken',
        'detected_flags',
        'created_at'
    ]
    list_filter = ['action_taken', 'strike_number', 'created_at']
    search_fields = ['original_sender__username', 'original_text']
    readonly_fields = ['created_at']