import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
if os.path.exists(BASE_DIR / '.env'):
    import environ
    env = environ.Env()
    environ.Env.read_env(BASE_DIR / '.env')
else:
    raise Exception("Could not find .env file")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'crispy_forms',
    'crispy_bootstrap5',
    # Local apps
    'core',
    'users',
    'products',
    # 'cart',
    'cart.apps.CartConfig',
    'orders',
    'payments',
    'wishlist',
    'api',
    'reviews',

    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    # 'allauth',
    # 'allauth.account',
    'social_django',
    # 'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.facebook',
    'ckeditor',
    'debug_toolbar',
    'robots',

]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

SITE_ID = 1

# Updated allauth configuration
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Use email for authentication
ACCOUNT_EMAIL_REQUIRED = True           # Email is required
ACCOUNT_UNIQUE_EMAIL = True              # Ensure email is unique
ACCOUNT_EMAIL_VERIFICATION = 'mandatory' # Require email verification
ACCOUNT_USERNAME_REQUIRED = False        # Username not required
AUTH_USER_MODEL = 'users.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.authentication.EmailBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'allauth.account.middleware.AccountMiddleware',

]

ROOT_URLCONF = 'Pochondo_E_Commerce.urls'

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

WSGI_APPLICATION = 'Pochondo_E_Commerce.wsgi.application'

DOMAIN = 'http://localhost:8000'
# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR/'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = 'core:index'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'FIELDS': ['id', 'email', 'name'],
        'VERIFIED_EMAIL': True,
    }
}

LOGOUT_REDIRECT_URL = 'core:index'

# Add this line
LOGIN_URL = '/users/login/'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')
SERVER_EMAIL = env('EMAIL_HOST_USER')
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']