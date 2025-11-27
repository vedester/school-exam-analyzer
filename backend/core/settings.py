import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv 

# Load the .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key')

# SECURITY WARNING: don't run with debug turned on in production!
# On Render, set the Environment Variable DEBUG = False
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# ALLOWED_HOSTS
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

     # Third Party Apps
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',

    # My Custom Apps
    'analytics',

    # Cleanup must be last
    'django_cleanup.apps.CleanupConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # 1. Whitenoise (Static Files)
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    
    # 2. CORS (Frontend Connection)
    'corsheaders.middleware.CorsMiddleware',
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# --- DATABASE CONFIGURATION (FIXED) ---
import dj_database_url

# 1. Get the Database URL
db_url = os.getenv("DATABASE_URL")

# 2. Smart Logic: Check if it's actually a Postgres URL before applying SSL
if db_url and "postgres" in db_url:
    # Production (Render)
    DATABASES = {
        'default': dj_database_url.config(
            default=db_url,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True, # Required for Render Postgres
        )
    }
else:
    # Local Development (SQLite)
    # This prevents the "sslmode" error
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
# --- END DATABASE CONFIGURATION ---


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES (CSS) ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Compression and Caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CORS SETTINGS (Simplified for Deployment) ---
# Allow all origins for the first deployment to ensure Vercel connects.
# You can restrict this later once you have your permanent Vercel domain.
CORS_ALLOW_ALL_ORIGINS = True 

# Trust Render for CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://school-exam-analyzer.onrender.com",
    "http://localhost:3000",
]

# --- FILE UPLOAD SETTINGS ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
os.makedirs(MEDIA_ROOT, exist_ok=True)

# --- REST FRAMEWORK ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), 
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# --- LOGGING (Optional but helpful) ---
import logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}