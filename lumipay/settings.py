from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from django.conf.global_settings import AUTH_USER_MODEL, SECRET_KEY
from decouple import config
import os
import dj_database_url
from rest_framework.permissions import IsAuthenticated


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing from environment variables.")


DEBUG = os.environ.get("DEBUG")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local apps
    "users",
    "security",
    "accounts",
    "transactions",
    "bills",
    "cards",
    "providers",
    "payments",

    # Third-party apps
    "rest_framework",
    "rest_framework.authtoken",
]


REST_FRAMEWORK = {
        "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
        "NON_FIELD_ERRORS_KEY": "errors",

        # for authentication
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.TokenAuthentication",
            # for simple jwt authentication
            "rest_framework_simplejwt.authentication.JWTAuthentication"
        ),
        # for permissions
        "DEFAULT_PERMISSION_CLASSES":(
            "rest_framework.permissions.IsAuthenticated",
            # "rest_framework.permissions.AllowAny",
        ),

    # 🚦 Throttling config
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.UserRateThrottle",
            "rest_framework.throttling.AnonRateThrottle",
        ],

        "DEFAULT_THROTTLE_RATES": {
            "anon": "5/minute",   # Unauthenticated users
            "user": "10/minute",  # Authenticated users
            "login": "3/minute",  # Custom for login endpoint
        },

        "EXCEPTION_HANDLER": "users.exceptions.custom_exception_handler",
}





MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lumipay.urls"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


AUTH_USER_MODEL = "users.User"



TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "lumipay.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),  # Reads from .env
        conn_max_age=600,                # Keeps DB connection alive for performance
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
