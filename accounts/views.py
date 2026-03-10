from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
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


@ratelimit(key='ip', rate='5/h', method='POST')
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
    # Check rate limit
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return Response(
            {"error": "Too many registration attempts. Try again later."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    serializer = UserRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = serializer.validated_data
    password = data['password']
    
    # Validate password strength
    try:
        validate_password(password)
    except DjangoValidationError as e:
        return Response(
            {"error": "Password validation failed", "details": list(e.messages)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Additional password checks
    if not any(c.isdigit() for c in password):
        return Response(
            {"error": "Password must contain at least one number"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not any(c.isupper() for c in password):
        return Response(
            {"error": "Password must contain at least one uppercase letter"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not any(c.islower() for c in password):
        return Response(
            {"error": "Password must contain at least one lowercase letter"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
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
    
    # Send SMS
    from .sms_service import termii_service
    sms_result = termii_service.send_verification_code(data['phone_number'], verification_code)
    
    if not sms_result['success']:
        print(f"SMS failed: {sms_result['error']}")
    
    print(f"Verification code for {data['phone_number']}: {verification_code}")
    
    return Response({
        "user_id": user.id,
        "message": "Verification code sent to your phone",
        "phone_masked": f"***{data['phone_number'][-4:]}",
        # REMOVE THIS IN PRODUCTION:
        "verification_code": verification_code if settings.DEBUG else None
    }, status=status.HTTP_201_CREATED)


@ratelimit(key='ip', rate='10/h', method='POST')
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
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return Response(
            {"error": "Too many verification attempts. Try again later."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
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
        from .sms_service import termii_service
        sms_result = termii_service.send_verification_code(profile.phone_number, verification_code)
        
        if not sms_result['success']:
            print(f"SMS failed: {sms_result['error']}")
        
        print(f"New verification code for {profile.phone_number}: {verification_code}")
        
        return Response({
            "message": "Verification code resent",
            # REMOVE IN PRODUCTION:
            "verification_code": verification_code if settings.DEBUG else None
        }, status=status.HTTP_200_OK)
        
    except Profile.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@ratelimit(key='ip', rate='10/m', method='POST')
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
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return Response(
            {"error": "Too many login attempts. Try again in 1 minute."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout user by blacklisting refresh token
    
    POST /api/auth/logout/
    Body: {"refresh_token": "..."}
    """
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )
        
    except TokenError:
        return Response(
            {"error": "Invalid or expired token"},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response({"error": "Phone number required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        profile = Profile.objects.get(phone_number=phone_number)
        reset_code = str(random.randint(100000, 999999))
        profile.verification_code = reset_code
        profile.verification_code_created_at = timezone.now()
        profile.save()
        
        from .sms_service import termii_service
        from django.conf import settings
        sms_result = termii_service.send_password_reset_code(phone_number, reset_code)
        if not sms_result['success']:
            print(f"SMS failed: {sms_result['error']}")
        print(f"Password reset code for {phone_number}: {reset_code}")
        
        return Response({"message": "Reset code sent to your phone", "phone_masked": f"***{phone_number[-4:]}", "reset_code": reset_code if settings.DEBUG else None})
    except Profile.DoesNotExist:
        return Response({"error": "Phone number not registered"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    phone_number = request.data.get('phone_number')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    
    if not all([phone_number, code, new_password]):
        return Response({"error": "All fields required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        profile = Profile.objects.get(phone_number=phone_number)
        if profile.verification_code != code:
            return Response({"error": "Invalid reset code"}, status=status.HTTP_400_BAD_REQUEST)
        
        code_age = timezone.now() - profile.verification_code_created_at
        if code_age > timedelta(minutes=10):
            return Response({"error": "Reset code expired"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validate_password(new_password)
        except DjangoValidationError as e:
            return Response({"error": "Password validation failed", "details": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
        
        if not any(c.isdigit() for c in new_password):
            return Response({"error": "Password must contain at least one number"}, status=status.HTTP_400_BAD_REQUEST)
        if not any(c.isupper() for c in new_password):
            return Response({"error": "Password must contain at least one uppercase letter"}, status=status.HTTP_400_BAD_REQUEST)
        if not any(c.islower() for c in new_password):
            return Response({"error": "Password must contain at least one lowercase letter"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = profile.user
        user.set_password(new_password)
        user.save()
        profile.verification_code = ''
        profile.save()
        
        return Response({"message": "Password reset successful. You can now login with your new password."})
    except Profile.DoesNotExist:
        return Response({"error": "Phone number not registered"}, status=status.HTTP_404_NOT_FOUND)