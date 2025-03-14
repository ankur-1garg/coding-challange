"""
Django settings for order_prj project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Snowflake Configuration
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_NAME = os.getenv('SNOWFLAKE_NAME')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ahk7xwo21&13u$_nugr4!&2mx804u617bpp$)$u3b=#yi6bm5h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Add these service URLs after the ALLOWED_HOSTS setting
CUSTOMER_SERVICE_URL = 'http://localhost:8001'
PRODUCT_SERVICE_URL = 'http://localhost:8002'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "order_app",
    "rest_framework",
    'rest_framework.authtoken',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'order_prj.urls'

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

WSGI_APPLICATION = 'order_prj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_snowflake',
        'NAME': os.getenv('SNOWFLAKE_NAME'),
        'SCHEMA': os.getenv('SNOWFLAKE_SCHEMA'),
        'WAREHOUSE': os.getenv('SNOWFLAKE_WAREHOUSE'),
        'USER': os.getenv('SNOWFLAKE_USER'),
        'PASSWORD': os.getenv('SNOWFLAKE_PASSWORD'),
        'ACCOUNT': os.getenv('SNOWFLAKE_ACCOUNT'),
        'OPTIONS': {
            'database': os.getenv('SNOWFLAKE_NAME'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA'),
            'role': 'ACCOUNTADMIN'
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Add CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Django REST framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# Service URLs (remove duplicate entries and fix paths)
# Remove /api as it's handled in views
CUSTOMER_SERVICE_URL = 'http://localhost:8001'
# Remove /api as it's handled in views
PRODUCT_SERVICE_URL = 'http://localhost:8002'
ORDER_SERVICE_URL = 'http://localhost:8003'

# Service timeout settings
SERVICE_TIMEOUT = 5  # seconds

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'WARNING',  # Change from DEBUG to WARNING to suppress SQL logs
            'propagate': False,
        },
    },
}

# Security settings
CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ['*']

# Session settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 hour

# Admin security settings
ADMIN_URL = 'order-admin/'
LOGIN_URL = 'admin:login'
ADMIN_SITE_HEADER = "Order Service Admin"
ADMIN_SITE_TITLE = "Order Service Administration"

# Service URLs and Settings
PRODUCT_SERVICE_URL = 'http://localhost:8002'
CUSTOMER_SERVICE_URL = 'http://localhost:8001'
SERVICE_HEALTH_CHECK_ENABLED = True
SERVICE_HEALTH_CHECK_TIMEOUT = 5  # seconds

# CSRF and CORS Settings
CSRF_TRUSTED_ORIGINS = [
    'http://ecommerce.local',
    'https://ecommerce.local',
    'http://localhost',
    'http://127.0.0.1'
]

CORS_ALLOWED_ORIGINS = [
    'http://ecommerce.local',
    'https://ecommerce.local',
    'http://localhost:8000',
    'http://127.0.0.1:8000'
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

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

# Security Settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True
CSRF_COOKIE_SAMESITE = 'Lax'
CORS_ALLOW_ALL_ORIGINS = False
