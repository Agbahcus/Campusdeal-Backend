# 🚨 DEPLOYMENT AUDIT REPORT - CRITICAL ISSUES

**Project:** CampusDeal Backend  
**Target:** Appliku + Hetzner Deployment  
**Date:** 2025  
**Status:** ⚠️ REQUIRES FIXES BEFORE DEPLOYMENT

---

## ✅ WHAT'S WORKING WELL

1. ✅ Good security practices with JWT authentication
2. ✅ Atomic database transactions for financial operations
3. ✅ Rate limiting configured
4. ✅ CORS properly configured
5. ✅ WhiteNoise for static files
6. ✅ PostgreSQL support via dj-database-url
7. ✅ Comprehensive wallet and withdrawal system
8. ✅ Paystack integration properly implemented

---

## 🔴 CRITICAL ISSUES (MUST FIX)

### 1. **SMS Service Not Configured for Sendchamp**

**Problem:** Your code still uses Termii, but your docs say you're using Sendchamp.

**Location:** `accounts/sms_service.py`

**Current Code:**
```python
class TermiiService:
    def __init__(self):
        self.api_key = settings.TERMII_API_KEY
        self.sender_id = settings.TERMII_SENDER_ID
        self.base_url = 'https://api.ng.termii.com/api'
```

**Fix Required:** Create `accounts/sendchamp_service.py`:
```python
import requests
from django.conf import settings

class SendchampService:
    def __init__(self):
        self.public_key = settings.SENDCHAMP_PUBLIC_KEY
        self.secret_key = settings.SENDCHAMP_SECRET_KEY
        self.sender_id = settings.SENDCHAMP_SENDER_ID
        self.base_url = settings.SENDCHAMP_BASE_URL
    
    def send_sms(self, phone_number, message):
        url = f'{self.base_url}/sms/send'
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'to': phone_number,
            'sender_name': self.sender_id,
            'message': message,
            'route': 'non_dnd'
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def send_verification_code(self, phone_number, code):
        message = f"Your CampusDeal verification code is: {code}. Valid for 10 minutes."
        return self.send_sms(phone_number, message)

sendchamp_service = SendchampService()
```

**Update settings.py:** Add Sendchamp config:
```python
# Sendchamp Configuration (SMS)
SENDCHAMP_PUBLIC_KEY = config('SENDCHAMP_PUBLIC_KEY', default='')
SENDCHAMP_SECRET_KEY = config('SENDCHAMP_SECRET_KEY', default='')
SENDCHAMP_SENDER_ID = config('SENDCHAMP_SENDER_ID', default='Sendchamp')
SENDCHAMP_BASE_URL = config('SENDCHAMP_BASE_URL', default='https://api.sendchamp.com/api/v1')
```

---

### 2. **Media Files Will Not Persist on Appliku**

**Problem:** You're using local filesystem for media files. Appliku containers are ephemeral - files will be deleted on restart.

**Location:** `settings.py`
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Fix Required:** Add Cloudinary support.

**Install dependency:**
```bash
pip install cloudinary django-cloudinary-storage
```

**Update settings.py:**
```python
# Add to INSTALLED_APPS (before django.contrib.staticfiles)
INSTALLED_APPS = [
    # ...
    'cloudinary_storage',
    'cloudinary',
    'django.contrib.staticfiles',
    # ...
]

# Cloudinary Configuration
import cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Use Cloudinary for media files in production
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    # Local storage for development
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
```

**Update requirements.txt:**
```
cloudinary==1.41.0
django-cloudinary-storage==0.3.0
```

---

### 3. **Missing Production Security Settings**

**Problem:** Security settings are not enforced in production.

**Location:** `settings.py` - Missing security headers

**Fix Required:** Add to `settings.py`:
```python
# Production Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Update CSRF_TRUSTED_ORIGINS for your domain
    CSRF_TRUSTED_ORIGINS = [
        'https://api.paystack.co',
        'https://*.appliku.app',  # Add your Appliku domain
        # Add your custom domain when you have one
    ]
```

---

### 4. **ALLOWED_HOSTS Needs Update**

**Problem:** Hardcoded domains won't work for Appliku.

**Current:**
```python
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,campusdeal-backend.onrender.com',
    cast=Csv(),
)
```

**Fix:** Update `.env`:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,*.appliku.app,your-custom-domain.com
```

---

### 5. **Database Connection Pooling Missing**

**Problem:** No connection pooling for PostgreSQL can cause connection exhaustion.

**Fix Required:** Install `psycopg2-pool` or use `django-db-pool`:

**Option 1 - Simple (Recommended):**
Update `settings.py`:
```python
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,  # Already good
            conn_health_checks=True,  # Already good
        )
    }
    DATABASES['default']['ATOMIC_REQUESTS'] = True
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000'  # 30 second query timeout
    }
```

---

### 6. **Missing Health Check Endpoint**

**Problem:** Appliku needs a health check endpoint to monitor your app.

**Fix Required:** Create `campusdeal/health.py`:
```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "healthy", "database": "connected"})
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=503)
```

**Add to `campusdeal/urls.py`:**
```python
from .health import health_check

urlpatterns = [
    path('health/', health_check),
    # ... existing urls
]
```

---

### 7. **Logging Not Configured for Production**

**Problem:** No logging configuration means you'll be blind to errors in production.

**Fix Required:** Add to `settings.py`:
```python
# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if not DEBUG else 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'marketplace': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

### 8. **Environment Variables Validation Missing**

**Problem:** App will start even if critical env vars are missing.

**Fix Required:** Add to `settings.py` (at the bottom):
```python
# Validate critical environment variables in production
if not DEBUG:
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'PAYSTACK_SECRET_KEY',
        'PAYSTACK_PUBLIC_KEY',
        'SENDCHAMP_SECRET_KEY',
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET',
    ]
    
    missing_vars = [var for var in required_vars if not config(var, default='')]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
```

---

### 9. **Dockerfile Needs Optimization**

**Current Dockerfile Issues:**
- Runs migrations in CMD (should be separate)
- Creates categories in CMD (should be management command)
- No health check

**Fix Required:** Update `Dockerfile`:
```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=5)"

# Run gunicorn
CMD gunicorn campusdeal.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -
```

**Create separate migration script** `migrate.sh`:
```bash
#!/bin/bash
python manage.py migrate --noinput
python manage.py shell -c "
from marketplace.models import ItemCategory
categories = ['Electronics', 'Books', 'Clothing', 'Furniture', 'Phones', 'Laptops', 'Accessories', 'Other']
for cat in categories:
    ItemCategory.objects.get_or_create(name=cat)
"
```

---

### 10. **CORS Configuration Too Permissive**

**Problem:** CORS allows credentials but origins are not properly validated.

**Current:**
```python
CORS_ALLOW_CREDENTIALS = True
```

**Fix Required:** Update `settings.py`:
```python
# CORS Settings
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:8081',
    cast=Csv()
)

CORS_ALLOW_CREDENTIALS = True

# Additional CORS security
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
```

---

## ⚠️ MEDIUM PRIORITY ISSUES

### 11. **No Rate Limiting on Critical Endpoints**

**Problem:** Withdrawal and payment endpoints have no rate limiting.

**Fix:** Add to withdrawal and payment views:
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='5/h', method='POST')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_funds(request):
    # ... existing code
```

---

### 12. **Missing Sentry for Error Tracking**

**Fix:** Add to `requirements.txt`:
```
sentry-sdk==1.40.0
```

**Add to `settings.py`:**
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=config('SENTRY_DSN', default=''),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production'
    )
```

---

### 13. **No Database Backup Strategy**

**Recommendation:** Set up automated backups on Hetzner:
- Daily PostgreSQL dumps
- Store in S3 or Hetzner Object Storage
- Retention: 30 days

---

### 14. **Missing Admin Notifications**

**Problem:** No alerts for critical events (failed withdrawals, high-value transactions).

**Recommendation:** Add webhook notifications or email alerts for:
- Withdrawal failures
- Transactions > ₦100,000
- Multiple failed login attempts
- Database connection issues

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### Code Changes Required:
- [ ] Replace Termii with Sendchamp service
- [ ] Add Cloudinary for media storage
- [ ] Add production security settings
- [ ] Add health check endpoint
- [ ] Add logging configuration
- [ ] Add environment variable validation
- [ ] Update Dockerfile
- [ ] Add rate limiting to critical endpoints
- [ ] Add Sentry integration

### Configuration Required:
- [ ] Generate new SECRET_KEY for production
- [ ] Set DEBUG=False in production .env
- [ ] Configure ALLOWED_HOSTS with Appliku domain
- [ ] Set up Cloudinary account and add credentials
- [ ] Set up Sendchamp account and add credentials
- [ ] Configure CORS_ALLOWED_ORIGINS with frontend domain
- [ ] Set up Sentry and add DSN
- [ ] Configure database connection string from Hetzner

### Infrastructure Setup:
- [ ] Create PostgreSQL database on Hetzner
- [ ] Set up automated database backups
- [ ] Configure Appliku deployment
- [ ] Set up custom domain (optional)
- [ ] Configure SSL certificate
- [ ] Set up monitoring (UptimeRobot or similar)

### Testing Required:
- [ ] Test SMS sending with Sendchamp
- [ ] Test image upload to Cloudinary
- [ ] Test payment flow with Paystack
- [ ] Test withdrawal flow
- [ ] Test health check endpoint
- [ ] Load test critical endpoints
- [ ] Test database failover

---

## 🚀 DEPLOYMENT STEPS

1. **Fix all critical issues** (items 1-10 above)
2. **Update requirements.txt** with new dependencies
3. **Test locally** with production-like settings
4. **Push to GitHub**
5. **Create Hetzner PostgreSQL database**
6. **Configure Appliku:**
   - Connect to GitHub repo
   - Set all environment variables
   - Configure build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Configure start command: `gunicorn campusdeal.wsgi:application --bind 0.0.0.0:$PORT --workers 4`
7. **Deploy to Appliku**
8. **Run migrations:** `python manage.py migrate`
9. **Create superuser:** `python manage.py createsuperuser`
10. **Test all endpoints**
11. **Monitor logs for errors**

---

## 📊 ESTIMATED TIME TO FIX

- Critical Issues (1-10): **4-6 hours**
- Medium Priority (11-14): **2-3 hours**
- Testing: **2-3 hours**
- **Total: 8-12 hours**

---

## 💡 RECOMMENDATIONS

1. **Start with critical issues 1-5** (most important)
2. **Test each fix locally** before deploying
3. **Deploy to staging first** if possible
4. **Monitor closely** for first 24 hours after deployment
5. **Have rollback plan ready**

---

**Status:** Ready to fix! All issues are documented with solutions.
