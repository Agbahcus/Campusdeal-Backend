from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
    """Profile serializer with user details"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'user_type',
            'phone_number',
            'phone_verified',
            'primary_location',
            'profile_picture',
            'university',
            'bio',
            'wallet_balance',
            'rating',
            'total_ratings',
            'chat_strikes',
            'is_suspended',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'phone_verified',
            'wallet_balance',
            'rating',
            'total_ratings',
            'chat_strikes',
            'is_suspended',
            'created_at',
            'updated_at'
        ]


class UserRegistrationSerializer(serializers.Serializer):
    """Serializer for user registration"""
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=8)
    primary_location = serializers.ChoiceField(
        choices=['ilorin', 'malete', 'offa', 'lagos', 'abuja', 'ibadan', 'kano', 'port-harcourt']
    )
    user_type = serializers.ChoiceField(
        choices=['student', 'landlord'],
        default='student'
    )
    
    def validate_phone_number(self, value):
        """Validate phone number format and uniqueness"""
        # Remove spaces and dashes
        phone = value.replace(' ', '').replace('-', '')
        
        # Check if already exists
        if Profile.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        
        return phone
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value


class PhoneVerificationSerializer(serializers.Serializer):
    """Serializer for phone verification"""
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
