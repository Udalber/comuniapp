"""
Django settings for ComuniApp — Librería Virtual Comunitaria.
"""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

_DEV_SECRET_KEY = "django-insecure-comuniapp-dev-only-change-before-deploy"

SECRET_KEY = os.environ.get("SECRET_KEY", _DEV_SECRET_KEY)

DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")

if not DEBUG and (not os.environ.get("SECRET_KEY") or SECRET_KEY == _DEV_SECRET_KEY):
    raise ImproperlyConfigured(
        "SECRET_KEY debe definirse en el entorno cuando DEBUG=False."
    )

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "https://*.onrender.com",
    ).split(",")
    if origin.strip()
]

# Render termina TLS en el proxy; necesario para cookies seguras y redirects HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "core",
    "accounts",
    "catalog",
    "cart",
    "orders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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
                "cart.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "accounts.User"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

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

LANGUAGE_CODE = "es-co"

TIME_ZONE = "America/Bogota"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Manifest + compresión solo en producción (requiere collectstatic).
_STATICFILES_BACKEND = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
    if DEBUG
    else "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": _STATICFILES_BACKEND,
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "catalog:index"
LOGOUT_REDIRECT_URL = "core:home"

AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Email — consola en desarrollo (confirmación de pedidos, sesión D)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@comuniapp.local"

# Costo fijo de envío en COP (subtotal carrito + SHIPPING_COST = total pedido)
SHIPPING_COST = 8_000
