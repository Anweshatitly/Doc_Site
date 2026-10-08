"""
Django settings for skincare_clinic project.
Uses python-decouple for environment variable management.
"""
import os
from pathlib import Path
from decouple import config, Csv

# ──────────────────────────────────────────────
# BASE DIRECTORY
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────
# SECURITY
# ──────────────────────────────────────────────
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver', cast=Csv())
if DEBUG and 'testserver' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('testserver')

# ──────────────────────────────────────────────
# INSTALLED APPS
# ──────────────────────────────────────────────
INSTALLED_APPS = [
    # Django built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',

    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',
    'django_cleanup.apps.CleanupConfig',

    # Project apps
    'core.apps.CoreConfig',
    'treatments.apps.TreatmentsConfig',
    'doctors.apps.DoctorsConfig',
    'appointments.apps.AppointmentsConfig',
    'blog.apps.BlogConfig',
    'gallery.apps.GalleryConfig',
]

# ──────────────────────────────────────────────
# MIDDLEWARE
# ──────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'skincare_clinic.urls'

# ──────────────────────────────────────────────
# TEMPLATES
# ──────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.clinic_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'skincare_clinic.wsgi.application'

# ──────────────────────────────────────────────
# DATABASE
# ──────────────────────────────────────────────
USE_SQLITE = config('USE_SQLITE', default=True, cast=bool)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

# ──────────────────────────────────────────────
# PASSWORD VALIDATION
# ──────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────────────────────────────────────
# INTERNATIONALIZATION
# ──────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────
# STATIC FILES
# ──────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ──────────────────────────────────────────────
# MEDIA FILES
# ──────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ──────────────────────────────────────────────
# DEFAULT PRIMARY KEY
# ──────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────────
# CRISPY FORMS
# ──────────────────────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ──────────────────────────────────────────────
# MESSAGES FRAMEWORK — BOOTSTRAP TAGS
# ──────────────────────────────────────────────
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ──────────────────────────────────────────────
# CLINIC CONFIGURATION (from .env)
# ──────────────────────────────────────────────
CLINIC_NAME = config('CLINIC_NAME', default='Skin & Hair Care Clinic')
CLINIC_PHONE = config('CLINIC_PHONE', default='')
CLINIC_WHATSAPP = config('CLINIC_WHATSAPP', default='+919876543210')
CLINIC_EMAIL = config('CLINIC_EMAIL', default='')
CLINIC_ADDRESS = config('CLINIC_ADDRESS', default='')

# ──────────────────────────────────────────────
# ADMIN URL (configurable via .env to obscure standard path)
# ──────────────────────────────────────────────
ADMIN_URL = config('DJANGO_ADMIN_URL', default='admin/')

# ──────────────────────────────────────────────
# SECURITY SETTINGS (Global Baseline)
# ──────────────────────────────────────────────
# Mitigate XSS stealing session cookies
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Clickjacking and MIME-type sniffing defense
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Upload limits (defend against memory/disk exhaustion DoS attacks)
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB max memory buffer
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB max request body
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# ──────────────────────────────────────────────
# SECURITY SETTINGS (Production Hardening)
# ──────────────────────────────────────────────
if not DEBUG:
    # Fail fast if deployment has an insecure secret key
    if not SECRET_KEY or SECRET_KEY.startswith('django-insecure-') or len(SECRET_KEY) < 50:
        raise ValueError(
            "CRITICAL SECURITY CONFIGURATION ERROR: "
            "DJANGO_SECRET_KEY must be a cryptographically secure random string with at least 50 characters in production."
        )
    if not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS:
        raise ValueError(
            "CRITICAL SECURITY CONFIGURATION ERROR: "
            "DJANGO_ALLOWED_HOSTS cannot be empty or contain wildcard '*' in production."
        )

    # Secure HTTPS-only cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # SSL Redirection and Reverse Proxy headers
    SECURE_SSL_REDIRECT = config('DJANGO_SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # HTTP Strict Transport Security (HSTS)
    SECURE_HSTS_SECONDS = config('DJANGO_SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
