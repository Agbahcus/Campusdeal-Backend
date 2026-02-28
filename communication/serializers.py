from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Chat, Message, ModeratedMessageLog
from accounts.serializers import UserSerializer
from marketplace.models import ItemListing


class ChatParticipantSerializer(serializers.ModelSerializer):
    """Lightweight serializer for chat participants"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    profile_picture = serializers.ImageField(
        source='profile.profile_picture',
        read_only=True
    )
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'profile_picture']


class ItemListingMinimalSerializer(serializers.ModelSerializer):
    """Minimal item info for chat context"""
    class Meta:
        model = ItemListing
        fields = ['id', 'title', 'price', 'image_1', 'status']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for individual messages"""
    sender = ChatParticipantSerializer(read_only=True)
    is_mine = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'text',
            'is_flagged',
            'flagged_for',
            'is_system_warning',
            'is_read',
            'created_at',
            'is_mine'
        ]
        read_only_fields = [
            'id',
            'sender',
            'is_flagged',
            'flagged_for',
            'is_system_warning',
            'created_at'
        ]
    
    def get_is_mine(self, obj):
        """Check if message is from current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False


class ChatSerializer(serializers.ModelSerializer):
    """Full chat serializer with participants and context"""
    participant_1 = ChatParticipantSerializer(read_only=True)
    participant_2 = ChatParticipantSerializer(read_only=True)
    related_item = ItemListingMinimalSerializer(read_only=True)
    other_participant = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = [
            'id',
            'participant_1',
            'participant_2',
            'other_participant',
            'related_item',
            'last_message',
            'last_message_time',
            'unread_count',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_message_time']
    
    def get_other_participant(self, obj):
        """Get the other participant in the chat"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other = obj.get_other_participant(request.user)
            return ChatParticipantSerializer(other).data
        return None
    
    def get_unread_count(self, obj):
        """Count unread messages for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                is_read=False
            ).exclude(
                sender=request.user
            ).count()
        return 0


class ChatListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for chat list"""
    other_participant = serializers.SerializerMethodField()
    related_item_title = serializers.CharField(
        source='related_item.title',
        read_only=True
    )
    related_item_image = serializers.ImageField(
        source='related_item.image_1',
        read_only=True
    )
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = [
            'id',
            'other_participant',
            'related_item_title',
            'related_item_image',
            'last_message',
            'last_message_time',
            'unread_count'
        ]
    
    def get_other_participant(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other = obj.get_other_participant(request.user)
            return {
                'id': other.id,
                'name': other.get_full_name(),
                'profile_picture': other.profile.profile_picture.url if other.profile.profile_picture else None
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                is_read=False
            ).exclude(
                sender=request.user
            ).count()
        return 0


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending messages"""
    text = serializers.CharField(max_length=2000)
    
    def validate_text(self, value):
        """Validate message is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class CreateChatSerializer(serializers.Serializer):
    """Serializer for creating new chat"""
    other_user_id = serializers.IntegerField()
    item_id = serializers.IntegerField(required=False)
    initial_message = serializers.CharField(
        max_length=2000,
        required=False,
        allow_blank=True
    )
    
    def validate_other_user_id(self, value):
        """Validate other user exists"""
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value
    
    def validate_item_id(self, value):
        """Validate item exists if provided"""
        if value:
            try:
                ItemListing.objects.get(id=value)
            except ItemListing.DoesNotExist:
                raise serializers.ValidationError("Item not found")
        return value


class ModeratedMessageLogSerializer(serializers.ModelSerializer):
    """Serializer for moderated message logs (admin use)"""
    sender_name = serializers.CharField(
        source='original_sender.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = ModeratedMessageLog
        fields = [
            'id',
            'original_sender',
            'sender_name',
            'chat',
            'original_text',
            'detected_flags',
            'action_taken',
            'strike_number',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']