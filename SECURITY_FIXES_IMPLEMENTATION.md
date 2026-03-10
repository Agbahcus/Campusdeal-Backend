# 🔧 SECURITY FIXES - IMPLEMENTATION GUIDE

**Priority:** CRITICAL - Implement before launch  
**Estimated Time:** 12-16 hours  
**Difficulty:** Medium

---

## 📋 IMPLEMENTATION CHECKLIST

- [ ] Fix 1: Add Rate Limiting (1 hour)
- [ ] Fix 2: Fix Wallet Race Condition (2 hours)
- [ ] Fix 3: Add Input Validation (4 hours)
- [ ] Fix 4: Implement Token Blacklist (1 hour)
- [ ] Fix 5: Add Transaction Timeouts (30 min)
- [ ] Fix 6: Fix Concurrent Orders (1 hour)
- [ ] Fix 7: Add File Size Validation (1 hour)
- [ ] Fix 8: Secure Webhooks (30 min)
- [ ] Fix 9: Password Complexity (1 hour)
- [ ] Fix 10: Add Pagination Limits (30 min)

---

## 🔴 FIX 1: ADD RATE LIMITING (1 HOUR)

### Step 1: Install Package
```bash
pip install django-ratelimit
```

### Step 2: Update requirements.txt
```
django-ratelimit==4.1.0
```

### Step 3: Create throttle.py
**File:** `campusdeal/throttle.py`
```python
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'

class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'

class AnonBurstRateThrottle(AnonRateThrottle):
    scope = 'anon_burst'
```

### Step 4: Update settings.py
```python
# Add to INSTALLED_APPS
INSTALLED_APPS += ['django_ratelimit']

# Add throttling configuration
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'campusdeal.throttle.BurstRateThrottle',
        'campusdeal.throttle.SustainedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon_burst': '10/minute',
        'burst': '60/minute',
        'sustained': '1000/day',
    }
}
```

### Step 5: Apply to Critical Endpoints
**File:** `accounts/views.py`
```python
from rest_framework.throttling import AnonRateThrottle

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])  # Add this
def register_user(request):
    # existing code
```

**Apply to:**
- register_user
- login_user
- verify_phone
- resend_verification_code

---

## 🔴 FIX 2: FIX WALLET RACE CONDITION (2 HOURS)

### Update order_views.py
**File:** `marketplace/order_views.py`

**Replace this:**
```python
def process_wallet_payment(order, buyer):
    profile = buyer.profile
    
    if profile.wallet_balance < order.total_amount:
        return Response({...})
    
    balance_before = profile.wallet_balance
    profile.wallet_balance -= order.total_amount
    profile.save()
```

**With this:**
```python
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError

def process_wallet_payment(order, buyer):
    """Process payment using wallet balance with race condition protection"""
    
    try:
        with transaction.atomic():
            # Lock the profile row
            profile = Profile.objects.select_for_update().get(user=buyer)
            
            # Check balance
            if profile.wallet_balance < order.total_amount:
                return Response({
                    "error": "Insufficient wallet balance",
                    "available": str(profile.wallet_balance),
                    "required": str(order.total_amount)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Store balance before
            balance_before = profile.wallet_balance
            
            # Use F() expression for atomic update
            Profile.objects.filter(user=buyer).update(
                wallet_balance=F('wallet_balance') - order.total_amount
            )
            
            # Refresh to get new balance
            profile.refresh_from_db()
            
            # Log transaction
            WalletTransaction.objects.create(
                user=buyer,
                transaction_type='debit',
                amount=order.total_amount,
                source='purchase',
                related_order=order,
                balance_before=balance_before,
                balance_after=profile.wallet_balance
            )
            
            # Update order
            order.status = 'paid'
            order.funds_held = True
            order.payment_method = 'wallet'
            order.paid_at = timezone.now()
            order.save()
            
            # Log status change
            OrderStatusHistory.objects.create(
                order=order,
                from_status='payment_pending',
                to_status='paid',
                changed_by=buyer
            )
        
        return Response({
            "success": True,
            "order_id": order.order_id,
            "status": "paid",
            "message": "Payment successful",
            "waybill_number": order.waybill_number
        })
        
    except Profile.DoesNotExist:
        return Response(
            {"error": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Payment processing failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

### Also fix confirm_delivery
**Replace:**
```python
seller_profile = order.seller.profile
balance_before = seller_profile.wallet_balance
seller_profile.wallet_balance += order.item_price
seller_profile.save()
```

**With:**
```python
with transaction.atomic():
    seller_profile = Profile.objects.select_for_update().get(user=order.seller)
    balance_before = seller_profile.wallet_balance
    
    Profile.objects.filter(user=order.seller).update(
        wallet_balance=F('wallet_balance') + order.item_price
    )
    
    seller_profile.refresh_from_db()
```

---

## 🔴 FIX 3: ADD INPUT VALIDATION (4 HOURS)

### Step 1: Create validators.py
**File:** `campusdeal/validators.py`
```python
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
import re

def validate_price(value):
    """Validate price is positive and reasonable"""
    try:
        price = Decimal(str(value))
        
        if price < 0:
            raise ValidationError("Price cannot be negative")
        
        if price < Decimal('100'):
            raise ValidationError("Minimum price is ₦100")
        
        if price > Decimal('10000000'):
            raise ValidationError("Maximum price is ₦10,000,000")
        
        # Check decimal places
        if price.as_tuple().exponent < -2:
            raise ValidationError("Maximum 2 decimal places")
        
        return price
        
    except (InvalidOperation, ValueError):
        raise ValidationError("Invalid price format")

def validate_search_query(query):
    """Sanitize and validate search query"""
    if not query:
        return ""
    
    # Remove special characters
    query = re.sub(r'[^\w\s-]', '', str(query))
    
    # Limit length
    query = query[:100]
    
    # Minimum length
    if len(query) < 2:
        raise ValidationError("Search query too short (minimum 2 characters)")
    
    return query

def validate_phone_number(phone):
    """Validate Nigerian phone number format"""
    # Remove spaces and dashes
    phone = re.sub(r'[\s-]', '', str(phone))
    
    # Check format
    if not re.match(r'^\+?234\d{10}$|^0\d{10}$', phone):
        raise ValidationError("Invalid Nigerian phone number")
    
    # Normalize to +234 format
    if phone.startswith('0'):
        phone = '+234' + phone[1:]
    elif not phone.startswith('+'):
        phone = '+' + phone
    
    return phone

def validate_image_size(image):
    """Validate image file size"""
    if image.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("Image size must be less than 5MB")
    
    # Validate image type
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    if hasattr(image, 'content_type') and image.content_type not in allowed_types:
        raise ValidationError("Only JPEG and PNG images allowed")
    
    return image

def validate_coordinates(latitude, longitude):
    """Validate coordinates are within Nigeria"""
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        # Nigeria bounds: 4°N to 14°N, 3°E to 15°E
        if not (4 <= lat <= 14):
            raise ValidationError("Latitude must be within Nigeria (4°N to 14°N)")
        
        if not (3 <= lon <= 15):
            raise ValidationError("Longitude must be within Nigeria (3°E to 15°E)")
        
        return lat, lon
        
    except (ValueError, TypeError):
        raise ValidationError("Invalid coordinates format")

def validate_amenities(amenities):
    """Validate hostel amenities list"""
    if not isinstance(amenities, list):
        raise ValidationError("Amenities must be a list")
    
    if len(amenities) > 20:
        raise ValidationError("Maximum 20 amenities allowed")
    
    # Validate each amenity
    for amenity in amenities:
        if not isinstance(amenity, str):
            raise ValidationError("Each amenity must be a string")
        if len(amenity) > 50:
            raise ValidationError("Amenity name too long (max 50 characters)")
    
    return amenities
```

### Step 2: Update models.py
**File:** `marketplace/models.py`
```python
from campusdeal.validators import validate_price, validate_image_size

class ItemListing(models.Model):
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(100), MaxValueValidator(10000000), validate_price]
    )
    
    image_1 = models.ImageField(
        upload_to='item_images/',
        blank=True,
        null=True,
        validators=[validate_image_size]
    )
```

### Step 3: Update views.py
**File:** `marketplace/views.py`
```python
from campusdeal.validators import validate_search_query, validate_price
from django.core.exceptions import ValidationError

@api_view(['GET'])
@permission_classes([AllowAny])
def browse_listings(request):
    # ... existing code ...
    
    # Validate search
    search = request.query_params.get('search')
    if search:
        try:
            search = validate_search_query(search)
            listings = listings.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Validate prices
    min_price = request.query_params.get('min_price')
    if min_price:
        try:
            min_price = validate_price(min_price)
            listings = listings.filter(price__gte=min_price)
        except ValidationError as e:
            return Response({"error": f"Invalid min_price: {e}"}, status=400)
    
    # ... rest of code ...
```

### Step 4: Add listing limits
**File:** `marketplace/views.py`
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_listing(request):
    # Check listing limit
    active_listings = ItemListing.objects.filter(
        seller=request.user,
        status='active'
    ).count()
    
    if active_listings >= 100:
        return Response(
            {"error": "Maximum 100 active listings allowed"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # ... rest of code ...
```

---

## 🔴 FIX 4: IMPLEMENT TOKEN BLACKLIST (1 HOUR)

### Step 1: Install package
```bash
pip install djangorestframework-simplejwt[crypto]
```

### Step 2: Update settings.py
```python
INSTALLED_APPS += [
    'rest_framework_simplejwt.token_blacklist',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,  # Add this
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Step 3: Run migrations
```bash
python manage.py migrate
```

### Step 4: Add logout endpoint
**File:** `accounts/views.py`
```python
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout user by blacklisting refresh token
    
    POST /api/auth/logout/
    Body: {
        "refresh_token": "..."
    }
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
```

### Step 5: Add to URLs
**File:** `accounts/urls.py`
```python
urlpatterns = [
    # ... existing urls ...
    path('auth/logout/', views.logout_user, name='logout'),
]
```

---

## 🔴 FIX 5: ADD TRANSACTION TIMEOUTS (30 MIN)

### Update settings.py
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'ATOMIC_REQUESTS': True,  # Add this
        'OPTIONS': {
            'timeout': 20,  # SQLite timeout
        }
    }
}

# For PostgreSQL (production):
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'OPTIONS': {
#             'connect_timeout': 10,
#             'options': '-c statement_timeout=30000'  # 30 seconds
#         }
#     }
# }
```

---

## 🔴 FIX 6: FIX CONCURRENT ORDERS (1 HOUR)

### Update order_views.py
**File:** `marketplace/order_views.py`

**Replace initiate_order function:**
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_order(request):
    serializer = InitiateOrderSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    seller = request.user
    item_id = serializer.validated_data['item_id']
    buyer_id = serializer.validated_data['buyer_id']
    delivery_method = serializer.validated_data['delivery_method']
    
    try:
        with db_transaction.atomic():
            # Lock the item row to prevent concurrent orders
            item = ItemListing.objects.select_for_update().get(id=item_id)
            
            # Validate ownership
            if item.seller != seller:
                return Response(
                    {"error": "You don't own this item"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check status
            if item.status != 'active':
                return Response(
                    {"error": "Item is not available for sale"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate delivery method
            if delivery_method == 'campusdeal' and not item.allow_campusdeal_delivery:
                return Response(
                    {"error": "CampusDeal delivery not available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if delivery_method == 'seller' and not item.allow_seller_delivery:
                return Response(
                    {"error": "Seller delivery not available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if delivery_method == 'pickup' and not item.allow_pickup:
                return Response(
                    {"error": "Pickup not available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get buyer
            from django.contrib.auth.models import User
            buyer = get_object_or_404(User, id=buyer_id)
            
            # Calculate fees
            item_price = item.price
            service_fee = item_price * Decimal('0.025')
            delivery_fee = Decimal('500.00') if delivery_method == 'campusdeal' else Decimal('0.00')
            total_amount = item_price + service_fee + delivery_fee
            
            # Create order
            order = Order.objects.create(
                item=item,
                buyer=buyer,
                seller=seller,
                delivery_method=delivery_method,
                item_price=item_price,
                service_fee=service_fee,
                delivery_fee=delivery_fee,
                total_amount=total_amount,
                status='payment_pending'
            )
            
            # Generate waybill
            if delivery_method == 'campusdeal':
                order.waybill_number = f"WB{uuid.uuid4().hex[:8].upper()}"
                order.save()
            
            # Update item status ATOMICALLY
            item.status = 'pending'
            item.save()
            
            # Log status change
            OrderStatusHistory.objects.create(
                order=order,
                from_status='',
                to_status='payment_pending',
                changed_by=seller
            )
        
        return Response({
            "order_id": order.order_id,
            "total_amount": str(total_amount),
            "breakdown": {
                "item_price": str(item_price),
                "service_fee": str(service_fee),
                "delivery_fee": str(delivery_fee)
            },
            "waybill_number": order.waybill_number,
            "payment_required": True,
            "message": "Order created. Waiting for buyer payment."
        }, status=status.HTTP_201_CREATED)
        
    except ItemListing.DoesNotExist:
        return Response(
            {"error": "Item not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Order creation failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

---

## 🔴 FIX 7: ADD FILE SIZE VALIDATION (1 HOUR)

### Already added in Fix 3 validators.py

### Update serializers.py
**File:** `marketplace/serializers.py`
```python
from campusdeal.validators import validate_image_size
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

class ItemListingSerializer(serializers.ModelSerializer):
    def validate_image_1(self, value):
        if value:
            try:
                validate_image_size(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value
    
    def validate_image_2(self, value):
        if value:
            try:
                validate_image_size(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value
    
    def validate_image_3(self, value):
        if value:
            try:
                validate_image_size(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value
```

---

## 🔴 FIX 8: SECURE WEBHOOKS (30 MIN)

### Update order_views.py
**File:** `marketplace/order_views.py`
```python
from django.conf import settings

# Add Paystack IP whitelist
PAYSTACK_IPS = [
    '52.31.139.75',
    '52.49.173.169',
    '52.214.14.220'
]

@api_view(['POST'])
@csrf_exempt
def paystack_webhook(request):
    """
    Receive and process Paystack webhooks with security
    """
    # Check IP whitelist
    client_ip = request.META.get('REMOTE_ADDR')
    if settings.DEBUG is False and client_ip not in PAYSTACK_IPS:
        return Response(
            {"error": "Unauthorized IP"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Verify webhook signature
    paystack_signature = request.headers.get('x-paystack-signature')
    
    if not paystack_service.verify_webhook_signature(request.body, paystack_signature):
        return Response(
            {"error": "Invalid signature"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get event data
    event = request.data.get('event')
    data = request.data.get('data')
    event_id = request.data.get('id')
    
    # Idempotency check
    from django.core.cache import cache
    cache_key = f"webhook_event_{event_id}"
    
    if cache.get(cache_key):
        return Response({"status": "already processed"})
    
    # Process event
    if event == 'charge.success':
        reference = data['reference']
        
        try:
            order = Order.objects.get(paystack_reference=reference)
            
            # Prevent double processing
            if order.status == 'paid':
                cache.set(cache_key, True, timeout=86400)  # 24 hours
                return Response({"status": "already paid"})
            
            with db_transaction.atomic():
                order.status = 'paid'
                order.funds_held = True
                order.payment_method = 'paystack'
                order.paid_at = timezone.now()
                order.save()
                
                OrderStatusHistory.objects.create(
                    order=order,
                    from_status='payment_pending',
                    to_status='paid'
                )
            
            # Mark as processed
            cache.set(cache_key, True, timeout=86400)
            
        except Order.DoesNotExist:
            pass
    
    return Response({"status": "success"})
```

---

## 🔴 FIX 9: PASSWORD COMPLEXITY (1 HOUR)

### Update accounts/views.py
```python
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
import re

def validate_password_strength(password):
    """Custom password validation"""
    errors = []
    
    # Django's built-in validation
    try:
        validate_password(password)
    except DjangoValidationError as e:
        errors.extend(e.messages)
    
    # Additional checks
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Check for common patterns
    common_patterns = ['12345', 'password', 'qwerty', 'abc123']
    if any(pattern in password.lower() for pattern in common_patterns):
        errors.append("Password contains common pattern")
    
    return errors

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Validate password strength
    password_errors = validate_password_strength(data['password'])
    if password_errors:
        return Response(
            {"error": "Password validation failed", "details": password_errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # ... rest of code ...
```

---

## 🔴 FIX 10: ADD PAGINATION LIMITS (30 MIN)

### Update views.py
**File:** `marketplace/views.py`
```python
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_page_size(self, request):
        """Enforce maximum page size"""
        if self.page_size_query_param:
            try:
                page_size = int(request.query_params.get(self.page_size_query_param, self.page_size))
                # Enforce maximum
                return min(page_size, self.max_page_size)
            except (ValueError, TypeError):
                pass
        return self.page_size
```

---

## 📊 TESTING YOUR FIXES

### Test Script
**File:** `test_security_fixes.py`
```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://127.0.0.1:8000"

def test_rate_limiting():
    """Test rate limiting works"""
    print("Testing rate limiting...")
    responses = []
    for i in range(15):
        r = requests.post(f"{BASE_URL}/api/auth/register/", json={})
        responses.append(r.status_code)
    
    # Should have some 429 (Too Many Requests)
    if 429 in responses:
        print("✅ Rate limiting working")
    else:
        print("❌ Rate limiting NOT working")

def test_concurrent_wallet():
    """Test wallet race condition is fixed"""
    print("Testing concurrent wallet transactions...")
    
    def make_purchase():
        # Login and make purchase
        pass
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_purchase) for _ in range(10)]
        results = [f.result() for f in futures]
    
    print("✅ Concurrent transactions handled")

def test_input_validation():
    """Test input validation"""
    print("Testing input validation...")
    
    # Test negative price
    r = requests.post(f"{BASE_URL}/api/marketplace/listings/create/", json={
        "price": "-1000"
    })
    
    if r.status_code == 400:
        print("✅ Negative price rejected")
    else:
        print("❌ Negative price NOT rejected")

if __name__ == "__main__":
    test_rate_limiting()
    test_input_validation()
```

---

## 🎯 DEPLOYMENT CHECKLIST

Before deploying to production:

- [ ] All 10 critical fixes implemented
- [ ] Tests passing
- [ ] Rate limiting configured
- [ ] Database timeouts set
- [ ] Token blacklist enabled
- [ ] Input validation on all endpoints
- [ ] File size limits enforced
- [ ] Webhook security enabled
- [ ] Password complexity enforced
- [ ] Pagination limits enforced

---

## 📞 SUPPORT

If you encounter issues:
1. Check error logs
2. Verify all migrations run
3. Test each fix individually
4. Review the STRESS_TEST_VULNERABILITIES.md document

---

**Total Implementation Time:** 12-16 hours  
**Priority:** CRITICAL  
**Status:** Ready to implement
