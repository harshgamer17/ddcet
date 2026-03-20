from pathlib import Path
import os

# ======================================================
# 📁 BASE DIRECTORY
# ======================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================================
# 🔐 SECURITY
# ======================================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key')

DEBUG = False

ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']

# ======================================================
# 📦 INSTALLED APPS
# ======================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'ddcetapp1',
]

# ======================================================
# ⚙️ MIDDLEWARE
# ======================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Static files fix (IMPORTANT)
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ======================================================
# 🔗 URL CONFIG
# ======================================================
ROOT_URLCONF = 'ddcetpro1.urls'

# ======================================================
# 🎨 TEMPLATES
# ======================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'ddcetapp1/templates'],
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

# ======================================================
# 🗄️ DATABASE
# ======================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ======================================================
# 🔑 PASSWORD VALIDATION
# ======================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'ddcetapp1.validators.CustomPasswordValidator',
    },
]

# ======================================================
# 🌍 LANGUAGE & TIMEZONE
# ======================================================
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True
USE_TZ = True

# ======================================================
# 📁 STATIC FILES
# ======================================================
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'ddcetapp1/static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ======================================================
# 🔐 LOGIN SETTINGS
# ======================================================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ======================================================
# 📧 EMAIL CONFIG (OTP SYSTEM)
# ======================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ======================================================
# 🔒 SECURITY SETTINGS (PRODUCTION)
# ======================================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS (Render auto SSL handle karega)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# ======================================================
# 🔧 DEFAULT AUTO FIELD
# ======================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'