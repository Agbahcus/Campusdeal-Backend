from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Chat, Message, ModeratedMessageLog
from .content_moderator import moderator
from .serializers import (
    ChatSerializer,
    ChatListSerializer,
    MessageSerializer,
    SendMessageSerializer,
    CreateChatSerializer,
    ModeratedMessageLogSerializer,
)
from marketplace.models import ItemListing
from .services import process_chat_message, mark_chat_messages_read
from marketplace.background_jobs import run_after_commit
from accounts.fcm_service import notify_user


class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============ CHAT MANAGEMENT ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_chats(request):
    """
    List all chats for current user

    GET /api/chats/
    """
    user = request.user
    chats = Chat.objects.filter(
        Q(participant_1=user) | Q(participant_2=user)
    ).select_related(
        'participant_1', 'participant_2',
        'participant_1__profile', 'participant_2__profile',
        'related_item'
    ).order_by('-last_message_time')

    serializer = ChatListSerializer(chats, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat(request):
    """
    Create new chat or return existing one

    POST /api/chats/create/
    Body: {
        "other_user_id": 123,
        "item_id": 456,
        "initial_message": "Is this still available?"
    }
    """
    serializer = CreateChatSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    other_user_id = serializer.validated_data['other_user_id']
    item_id = serializer.validated_data.get('item_id')
    initial_message = serializer.validated_data.get('initial_message', '')

    if other_user_id == user.id:
        return Response({'error': 'Cannot create chat with yourself'}, status=status.HTTP_400_BAD_REQUEST)

    if user.profile.is_suspended:
        return Response({'error': 'Your account is suspended. You cannot send messages.'}, status=status.HTTP_403_FORBIDDEN)

    other_user = get_object_or_404(User, id=other_user_id)

    if other_user.profile.is_suspended:
        return Response({'error': "Cannot start chat. The other user's account is suspended."}, status=status.HTTP_400_BAD_REQUEST)

    p1, p2 = (user, other_user) if user.id < other_user.id else (other_user, user)

    item = get_object_or_404(ItemListing, id=item_id) if item_id else None

    chat = Chat.objects.filter(participant_1=p1, participant_2=p2).first()
    is_new_chat = chat is None

    if not chat:
        chat = Chat.objects.create(participant_1=p1, participant_2=p2, related_item=item)

    if initial_message:
        message_result = process_chat_message(chat, user, initial_message)
        if not message_result['success']:
            return Response({
                'error': 'Message violates policy',
                'warning': message_result['warning'],
                'flags': message_result['flags'],
            }, status=status.HTTP_400_BAD_REQUEST)

    # Notify the other user if this is a new chat
    if is_new_chat:
        item_title = item.title if item else 'your listing'
        sender_name = user.get_full_name() or user.username
        run_after_commit(
            'new-chat-notify',
            notify_user,
            other_user,
            'New Message',
            f'{sender_name} started a conversation about {item_title}',
            notification_type='new_message',
            related_id=chat.id,
        )

    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat(request, chat_id):
    """
    GET /api/chats/{chat_id}/
    """
    chat = get_object_or_404(
        Chat.objects.select_related('participant_1', 'participant_2', 'related_item'),
        id=chat_id
    )
    if request.user not in [chat.participant_1, chat.participant_2]:
        return Response({'error': "You don't have access to this chat"}, status=status.HTTP_403_FORBIDDEN)

    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data)


# ============ MESSAGING ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, chat_id):
    """
    GET /api/chats/{chat_id}/messages/
    """
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in [chat.participant_1, chat.participant_2]:
        return Response({'error': "You don't have access to this chat"}, status=status.HTTP_403_FORBIDDEN)

    messages = chat.messages.select_related('sender').order_by('-created_at')
    paginator = MessagePagination()
    page = paginator.paginate_queryset(messages, request)

    if page is not None:
        serializer = MessageSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, chat_id):
    """
    POST /api/chats/{chat_id}/messages/send/
    Body: {"text": "Message content here"}
    """
    chat = get_object_or_404(Chat, id=chat_id)
    sender = request.user

    if sender not in [chat.participant_1, chat.participant_2]:
        return Response({'error': 'You are not a participant in this chat'}, status=status.HTTP_403_FORBIDDEN)

    if sender.profile.is_suspended:
        return Response({
            'error': 'Your account is suspended. You cannot send messages.',
            'reason': sender.profile.suspension_reason,
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = SendMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    message_text = serializer.validated_data['text']
    message_result = process_chat_message(chat, sender, message_text)

    if message_result['success']:
        # Notify recipient
        recipient = chat.get_other_participant(sender)
        sender_name = sender.get_full_name() or sender.username
        run_after_commit(
            'message-notify',
            notify_user,
            recipient,
            f'New message from {sender_name}',
            message_text[:80],
            notification_type='new_message',
            related_id=chat.id,
        )
        return Response(
            MessageSerializer(message_result['message'], context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    return Response({
        'error': 'Message blocked',
        'warning': message_result['warning'],
        'strike_number': message_result['strike_number'],
        'strikes_remaining': message_result['strikes_remaining'],
        'account_suspended': message_result['account_suspended'],
        'flags': message_result['flags'],
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_messages_read(request, chat_id):
    """
    PATCH /api/chats/{chat_id}/mark-read/
    """
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in [chat.participant_1, chat.participant_2]:
        return Response({'error': "You don't have access to this chat"}, status=status.HTTP_403_FORBIDDEN)

    updated = mark_chat_messages_read(chat, request.user)
    return Response({'success': True, 'messages_marked_read': updated})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    """
    GET /api/chats/unread-count/
    """
    user = request.user
    user_chats = Chat.objects.filter(Q(participant_1=user) | Q(participant_2=user))
    total_unread = Message.objects.filter(
        chat__in=user_chats, is_read=False
    ).exclude(sender=user).count()

    return Response({'unread_count': total_unread})


# ============ MODERATION (Admin) ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_moderation_logs(request):
    """
    GET /api/chats/moderation-logs/
    """
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    logs = ModeratedMessageLog.objects.select_related(
        'original_sender', 'chat'
    ).order_by('-created_at')[:100]

    serializer = ModeratedMessageLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_moderator(request):
    """
    POST /api/chats/test-moderator/ (DEBUG only)
    """
    from django.conf import settings
    if not settings.DEBUG:
        return Response({'error': 'Only available in debug mode'}, status=status.HTTP_403_FORBIDDEN)

    text = request.data.get('text', '')
    result = moderator.scan_message(text)
    return Response({'text': text, 'result': result})
