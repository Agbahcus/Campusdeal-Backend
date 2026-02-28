from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import random

from .models import Profile
from .serializers import (
    UserRegistrationSerializer,
    PhoneVerificationSerializer,
    LoginSerializer,
    ProfileSerializer,
    UserSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user with phone verification
    
    POST /api/auth/register/
    Body: {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone_number": "+2348012345678",
        "password": "securepass123",
        "primary_location": "ilorin",
        "user_type": "student"
    }
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = serializer.validated_data
    
    # Split full name
    name_parts = data['full_name'].split()
    first_name = name_parts[0]
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    
    # Create User
    user = User.objects.create_user(
        username=data['phone_number'],  # Use phone as username
        email=data['email'],
        password=data['password'],
        first_name=first_name,
        last_name=last_name
    )
    
    # Generate 6-digit verification code
    verification_code = str(random.randint(100000, 999999))
    
    # Create Profile
    profile = Profile.objects.create(
        user=user,
        phone_number=data['phone_number'],
        primary_location=data['primary_location'],
        user_type=data.get('user_type', 'student'),
        verification_code=verification_code,
        verification_code_created_at=timezone.now()
    )
    
    # TODO: Send SMS via Termii/Twilio
    # For now, we'll return the code in response (ONLY FOR DEVELOPMENT)
    # In production, remove this and only send via SMS
    
    print(f"Verification code for {data['phone_number']}: {verification_code}")
    
    return Response({
        "user_id": user.id,
        "message": "Verification code sent to your phone",
        "phone_masked": f"***{data['phone_number'][-4:]}",
        # REMOVE THIS IN PRODUCTION:
        "verification_code": verification_code  # Only for testing
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_phone(request):
    """
    Verify phone number with SMS code
    
    POST /api/auth/verify-phone/
    Body: {
        "user_id": 123,
        "code": "123456"
    }
    """
    serializer = PhoneVerificationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_id = serializer.validated_data['user_id']
    code = serializer.validated_data['code']
    
    try:
        profile = Profile.objects.get(user_id=user_id)
        
        # Check if already verified
        if profile.phone_verified:
            return Response(
                {"message": "Phone already verified"},
                status=status.HTTP_200_OK
            )
        
        # Check code validity
        if profile.verification_code != code:
            return Response(
                {"error": "Invalid verification code"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check code expiration (10 minutes)
        code_age = timezone.now() - profile.verification_code_created_at
        if code_age > timedelta(minutes=10):
            return Response(
                {"error": "Verification code expired. Request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark as verified
        profile.phone_verified = True
        profile.verification_code = ''  # Clear code
        profile.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(profile.user)
        
        return Response({
            "message": "Phone verified successfully",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": UserSerializer(profile.user).data,
            "profile": ProfileSerializer(profile).data
        }, status=status.HTTP_200_OK)
        
    except Profile.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_code(request):
    """
    Resend verification code
    
    POST /api/auth/resend-code/
    Body: {
        "user_id": 123
    }
    """
    user_id = request.data.get('user_id')
    
    try:
        profile = Profile.objects.get(user_id=user_id)
        
        if profile.phone_verified:
            return Response(
                {"message": "Phone already verified"},
                status=status.HTTP_200_OK
            )
        
        # Generate new code
        verification_code = str(random.randint(100000, 999999))
        profile.verification_code = verification_code
        profile.verification_code_created_at = timezone.now()
        profile.save()
        
        # TODO: Send SMS
        print(f"New verification code for {profile.phone_number}: {verification_code}")
        
        return Response({
            "message": "Verification code resent",
            # REMOVE IN PRODUCTION:
            "verification_code": verification_code
        }, status=status.HTTP_200_OK)
        
    except Profile.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login with phone number and password
    
    POST /api/auth/login/
    Body: {
        "phone_number": "+2348012345678",
        "password": "securepass123"
    }
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    phone_number = serializer.validated_data['phone_number']
    password = serializer.validated_data['password']
    
    # Authenticate using phone as username
    user = authenticate(username=phone_number, password=password)
    
    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if phone is verified
    if not user.profile.phone_verified:
        return Response(
            {
                "error": "Phone not verified",
                "user_id": user.id,
                "message": "Please verify your phone number first"
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if suspended
    if user.profile.is_suspended:
        return Response(
            {
                "error": "Account suspended",
                "reason": user.profile.suspension_reason
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        "message": "Login successful",
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "user": UserSerializer(user).data,
        "profile": ProfileSerializer(user.profile).data
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get or update current user's profile
    
    GET /api/users/me/
    PATCH /api/users/me/
    """
    profile = request.user.profile
    
    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Only allow updating certain fields
        allowed_fields = ['university', 'bio', 'profile_picture']
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = ProfileSerializer(profile, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request, user_id):
    """
    Get public profile of any user
    
    GET /api/users/{user_id}/profile/
    """
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
        
        # Return limited public info
        data = {
            "id": user.id,
            "full_name": user.get_full_name(),
            "profile_picture": profile.profile_picture.url if profile.profile_picture else None,
            "university": profile.university,
            "bio": profile.bio,
            "rating": str(profile.rating),
            "total_ratings": profile.total_ratings,
            "primary_location": profile.primary_location,
            "member_since": profile.created_at.strftime('%B %Y')
        }
        
        return Response(data)
        
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )