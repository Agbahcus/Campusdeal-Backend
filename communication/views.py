from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
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
    ModeratedMessageLogSerializer
)
from marketplace.models import ItemListing
from .services import process_chat_message, mark_chat_messages_read


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
    
    # Get all chats where user is a participant
    chats = Chat.objects.filter(
        Q(participant_1=user) | Q(participant_2=user)
    ).select_related(
        'participant_1',
        'participant_2',
        'participant_1__profile',
        'participant_2__profile',
        'related_item'
    ).order_by('-last_message_time')
    
    serializer = ChatListSerializer(
        chats,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat(request):
    """
    Create new chat or return existing one
    
    POST /api/chats/create/
    Body: {
        "other_user_id": 123,
        "item_id": 456,  // optional
        "initial_message": "Is this still available?"  // optional
    }
    """
    serializer = CreateChatSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    other_user_id = serializer.validated_data['other_user_id']
    item_id = serializer.validated_data.get('item_id')
    initial_message = serializer.validated_data.get('initial_message', '')
    
    # Can't chat with yourself
    if other_user_id == user.id:
        return Response(
            {"error": "Cannot create chat with yourself"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user is suspended
    if user.profile.is_suspended:
        return Response(
            {"error": "Your account is suspended. You cannot send messages."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    other_user = get_object_or_404(User, id=other_user_id)
    
    # Check if other user is suspended
    if other_user.profile.is_suspended:
        return Response(
            {"error": "Cannot start chat. The other user's account is suspended."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or create chat (ensure consistent ordering)
    # participant_1 is always the user with lower ID
    if user.id < other_user.id:
        p1, p2 = user, other_user
    else:
        p1, p2 = other_user, user
    
    item = None
    if item_id:
        item = get_object_or_404(ItemListing, id=item_id)
    
    # Check if chat already exists
    chat = Chat.objects.filter(
        participant_1=p1,
        participant_2=p2
    ).first()
    
    if not chat:
        # Create new chat
        chat = Chat.objects.create(
            participant_1=p1,
            participant_2=p2,
            related_item=item
        )
    
    # Send initial message if provided
    if initial_message:
        message_result = process_chat_message(chat, user, initial_message)
        if not message_result['success']:
            # Message violates policy - return error
            return Response({
                "error": "Message violates policy",
                "warning": message_result['warning'],
                "flags": message_result['flags']
            }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat(request, chat_id):
    """
    Get chat details
    
    GET /api/chats/{chat_id}/
    """
    chat = get_object_or_404(
        Chat.objects.select_related(
            'participant_1',
            'participant_2',
            'related_item'
        ),
        id=chat_id
    )
    
    # Verify user is participant
    if request.user not in [chat.participant_1, chat.participant_2]:
        return Response(
            {"error": "You don't have access to this chat"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data)


# ============ MESSAGING ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, chat_id):
    """
    Get messages in a chat
    
    GET /api/chats/{chat_id}/messages/
    Query params:
    - page: page number
    - page_size: messages per page (default 50)
    """
    chat = get_object_or_404(Chat, id=chat_id)
    
    # Verify user is participant
    if request.user not in [chat.participant_1, chat.participant_2]:
        return Response(
            {"error": "You don't have access to this chat"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get messages (newest first, but paginated)
    messages = chat.messages.select_related('sender').order_by('-created_at')
    
    # Paginate
    paginator = MessagePagination()
    page = paginator.paginate_queryset(messages, request)
    
    if page is not None:
        serializer = MessageSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)
    
    serializer = MessageSerializer(
        messages,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, chat_id):
    """
    Send a message with automatic moderation
    
    POST /api/chats/{chat_id}/messages/
    Body: {
        "text": "Message content here"
    }
    """
    chat = get_object_or_404(Chat, id=chat_id)
    sender = request.user
    
    # Verify sender is participant
    if sender not in [chat.participant_1, chat.participant_2]:
        return Response(
            {"error": "You are not a participant in this chat"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if sender is suspended
    if sender.profile.is_suspended:
        return Response({
            "error": "Your account is suspended. You cannot send messages.",
            "reason": sender.profile.suspension_reason
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = SendMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message_text = serializer.validated_data['text']
    
    message_result = process_chat_message(chat, sender, message_text)

    if message_result['success']:
        return Response(
            MessageSerializer(message_result['message'], context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    return Response({
        "error": "Message blocked",
        "warning": message_result['warning'],
        "strike_number": message_result['strike_number'],
        "strikes_remaining": message_result['strikes_remaining'],
        "account_suspended": message_result['account_suspended'],
        "flags": message_result['flags']
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_messages_read(request, chat_id):
    """
    Mark all messages in chat as read
    
    PATCH /api/chats/{chat_id}/mark-read/
    """
    chat = get_object_or_404(Chat, id=chat_id)
    
    # Verify user is participant
    if request.user not in [chat.participant_1, chat.participant_2]:
        return Response(
            {"error": "You don't have access to this chat"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    updated = mark_chat_messages_read(chat, request.user)
    
    return Response({
        "success": True,
        "messages_marked_read": updated
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    """
    Get total unread message count across all chats
    
    GET /api/chats/unread-count/
    """
    user = request.user
    
    # Get all chats where user is participant
    user_chats = Chat.objects.filter(
        Q(participant_1=user) | Q(participant_2=user)
    )
    
    # Count unread messages from others
    total_unread = Message.objects.filter(
        chat__in=user_chats,
        is_read=False
    ).exclude(sender=user).count()
    
    return Response({
        "unread_count": total_unread
    })


# ============ MODERATION (Admin) ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_moderation_logs(request):
    """
    Get moderation logs (admin only)
    
    GET /api/chats/moderation-logs/
    """
    if not request.user.is_staff:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    logs = ModeratedMessageLog.objects.select_related(
        'original_sender',
        'chat'
    ).order_by('-created_at')[:100]
    
    serializer = ModeratedMessageLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_moderator(request):
    """
    Test the content moderator (development only)
    
    POST /api/chats/test-moderator/
    Body: {
        "text": "Message to test"
    }
    """
    # Only allow in DEBUG mode
    from django.conf import settings
    if not settings.DEBUG:
        return Response(
            {"error": "Only available in debug mode"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    text = request.data.get('text', '')
    result = moderator.scan_message(text)
    
    return Response({
        "text": text,
        "result": result
    })
