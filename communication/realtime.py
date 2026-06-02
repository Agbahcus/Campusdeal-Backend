from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def chat_group_name(chat_id):
    return f'chat_{chat_id}'


def serialize_message(message):
    sender = message.sender
    profile_picture = None
    if hasattr(sender, 'profile') and sender.profile and sender.profile.profile_picture:
        profile_picture = sender.profile.profile_picture.url

    return {
        'id': message.id,
        'chat_id': message.chat_id,
        'sender': {
            'id': sender.id,
            'full_name': sender.get_full_name(),
            'profile_picture': profile_picture,
        },
        'text': message.text,
        'is_flagged': message.is_flagged,
        'flagged_for': message.flagged_for,
        'is_system_warning': message.is_system_warning,
        'is_read': message.is_read,
        'created_at': message.created_at.isoformat(),
    }


def broadcast_chat_message(chat, message, event_type='chat.message'):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    async_to_sync(channel_layer.group_send)(
        chat_group_name(chat.id),
        {
            'type': event_type,
            'payload': {
                'chat_id': chat.id,
                'message': serialize_message(message),
                'last_message': chat.last_message,
                'last_message_time': chat.last_message_time.isoformat() if chat.last_message_time else None,
            },
        },
    )


def broadcast_chat_read(chat, reader_id, unread_count):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    async_to_sync(channel_layer.group_send)(
        chat_group_name(chat.id),
        {
            'type': 'chat.read',
            'payload': {
                'chat_id': chat.id,
                'reader_id': reader_id,
                'unread_count': unread_count,
            },
        },
    )
