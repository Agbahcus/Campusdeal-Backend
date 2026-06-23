"""
Django settings for campusdeal project.
"""

from pathlib import Path
import os
from datetime import timedelta
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
def _parse_debug_flag(value, default=True):
    if value is None:
        return default

    normalized = str(value).strip().lower()
    if normalized in {'1', 'true', 't', 'yes', 'y', 'on'}:
        return True
    if normalized in {'0', 'false', 'f', 'no', 'n', 'off', 'release', 'prod', 'production', 'live'}:
        return False
    return default



DEBUG = _parse_debug_flag(os.environ.get('DEBUG'), default=False)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,campusdeal-backend.onrender.com',
    cast=Csv(),
)

# Rate Limiting & Caching
REDIS_URL_SETTING = os.environ.get('REDIS_URL', '')
if REDIS_URL_SETTING:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL_SETTING,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Application definition
OPTIONAL_APPS = []
try:
    import cloudinary  # type: ignore
    OPTIONAL_APPS.extend([
        'cloudinary_storage',
        'cloudinary',
    ])
except ModuleNotFoundError:
    cloudinary = None

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'channels',
    *OPTIONAL_APPS,

    # Local apps
    'accounts',
    'marketplace',
    'communication',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files
    'corsheaders.middleware.CorsMiddleware',  # CORS - must be high up
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CSRF Exemptions for webhooks
CSRF_TRUSTED_ORIGINS = [
    'https://api.paystack.co',
]

# Add production domains when DEBUG is False
if not DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        'https://*.appliku.app',
        'https://campusdeal.vercel.app',
        'https://campusdealls.netlify.app',
        'https://*.netlify.app',
    ])

ROOT_URLCONF = 'campusdeal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'campusdeal.wsgi.application'
ASGI_APPLICATION = 'campusdeal.asgi.application'

# Database
# Automatically uses Railway's DATABASE_URL in production
import dj_database_url

if 'DATABASE_URL' in os.environ:
    # Production: Use PostgreSQL from Railway
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    DATABASES['default']['ATOMIC_REQUESTS'] = True
    DATABASES['default']['OPTIONS'] = {'connect_timeout': 10}
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'ATOMIC_REQUESTS': True,
            'OPTIONS': {
                'timeout': 20,
            }
        }
    }

# Channels / websocket layer
REDIS_URL = config('REDIS_URL', default='')
if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'  # Nigerian timezone
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cloudinary Configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Media files (User uploads)
if not DEBUG and CLOUDINARY_STORAGE['CLOUD_NAME'] and cloudinary is not None:
    # Production: Use Cloudinary
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = '/media/'  # Cloudinary will handle this
else:
    # Development: Use local storage
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings (for frontend communication)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:8081,http://127.0.0.1:3000',
    cast=Csv()
)

CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://.*\.netlify\.app$',
]

CORS_ALLOW_CREDENTIALS = True

# SMS Configuration (Sendchamp for Nigeria)
SMS_PROVIDER = config('SMS_PROVIDER', default='sendchamp')

SENDCHAMP_ACCESS_KEY = config('SENDCHAMP_ACCESS_KEY', default='')
SENDCHAMP_PUBLIC_KEY = config('SENDCHAMP_PUBLIC_KEY', default='')
SENDCHAMP_SECRET_KEY = config('SENDCHAMP_SECRET_KEY', default='')
SENDCHAMP_SENDER_ID = config('SENDCHAMP_SENDER_ID', default='Sendchamp')
SENDCHAMP_BASE_URL = config('SENDCHAMP_BASE_URL', default='https://api.sendchamp.com/api/v1')

# SmartSMS (smartsms.ng)
SMARTSMS_USERNAME = config('SMARTSMS_USERNAME', default='')
SMARTSMS_API_KEY = config('SMARTSMS_API_KEY', default='')
SMARTSMS_SENDER_ID = config('SMARTSMS_SENDER_ID', default='CampusDeal')
SMARTSMS_BASE_URL = config('SMARTSMS_BASE_URL', default='https://www.smartsms.ng/api')
SMARTSMS_DNDSENDER = config('SMARTSMS_DNDSENDER', default=0, cast=int)

# Legacy Termii (keeping for backward compatibility, but not used)
TERMII_API_KEY = config('TERMII_API_KEY', default='')
TERMII_SENDER_ID = config('TERMII_SENDER_ID', default='CampusDeal')
TERMII_API_URL = 'https://api.ng.termii.com/api/sms/send'

# Payment Configuration (Paystack)
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY', default='')
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY', default='')
PAYSTACK_INITIALIZE_URL = 'https://api.paystack.co/transaction/initialize'
PAYSTACK_VERIFY_URL = 'https://api.paystack.co/transaction/verify'

# File Upload Settings
MAX_UPLOAD_SIZE = 5242880  # 5MB in bytes
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/jpg']

# FCM Push Notifications
FCM_SERVER_KEY = config('FCM_SERVER_KEY', default='')

# Frontend URL
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@campusdeal.com')
FINANCE_ALERT_EMAILS = [email.strip() for email in config('FINANCE_ALERT_EMAILS', default='').split(',') if email.strip()]

# Production Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
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
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'marketplace': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Sentry Configuration (Error Tracking)
if not DEBUG:
    SENTRY_DSN = config('SENTRY_DSN', default='')
    if SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.django import DjangoIntegration

            sentry_sdk.init(
                dsn=SENTRY_DSN,
                integrations=[DjangoIntegration()],
                traces_sample_rate=0.1,
                send_default_pii=False,
                environment='production'
            )
        except ModuleNotFoundError:
            pass

# Validate critical environment variables in production
if not DEBUG:
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'PAYSTACK_SECRET_KEY',
        'PAYSTACK_PUBLIC_KEY',
        'SENDCHAMP_SECRET_KEY',
    ]
    missing_vars = [var for var in required_vars if not config(var, default='')]
    if missing_vars:
        import logging
        logging.warning(f"Missing environment variables: {', '.join(missing_vars)}")
