"""Django settings for furniture_store project."""

from pathlib import Path
from urllib.parse import urlparse
import importlib
import os

_dj_database_url_spec = importlib.util.find_spec("dj_database_url")
if _dj_database_url_spec:
    dj_database_url = importlib.import_module("dj_database_url")
else:
    class _DjDatabaseUrlFallback:
        def config(self, *_, **__):
            raise ImportError(
                "dj-database-url is required when DATABASE_URL is set. "
                "Install it with `pip install dj-database-url`."
            )

    dj_database_url = _DjDatabaseUrlFallback()

_decouple_spec = importlib.util.find_spec("decouple")
if _decouple_spec:
    decouple = importlib.import_module("decouple")
    config = decouple.config
    Csv = decouple.Csv
else:
    def _to_bool(value):
        """Minimal bool caster similar to python-decouple."""
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "t", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "f", "no", "n", "off"}:
            return False
        raise ValueError(f"Invalid boolean value: {value}")

    def _apply_cast(value, cast):
        if cast in (None, str) or value is None:
            return value
        if cast is bool:
            return _to_bool(value)
        if isinstance(cast, type):
            return value if isinstance(value, cast) else cast(value)
        if callable(cast):
            return cast(value)
        return value

    class Csv:
        def __init__(self, delimiter=",", strip=True, ignore_empty=True):
            self.delimiter = delimiter
            self.strip = strip
            self.ignore_empty = ignore_empty

        def __call__(self, value):
            if value is None:
                return []
            if isinstance(value, (list, tuple)):
                return list(value)
            items = str(value).split(self.delimiter)
            if self.strip:
                items = [item.strip() for item in items]
            if self.ignore_empty:
                items = [item for item in items if item]
            return items

    def config(option, default=None, cast=str):
        raw = os.getenv(option)
        if raw is None:
            return _apply_cast(default, cast)
        return _apply_cast(raw, cast)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default="django-insecure-s*ju%pwu6c^n3nyza-4(w@qx_$$y_u5#=qpmt=-9049a^_8w95")
DEBUG = config('DEBUG', default=False, cast=bool)

_allowed_hosts = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
if DEBUG:
    if not _allowed_hosts:
        ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    else:
        ALLOWED_HOSTS = list(set(_allowed_hosts + ['localhost', '127.0.0.1']))
else:
    ALLOWED_HOSTS = _allowed_hosts if _allowed_hosts else []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "crispy_forms",
    "crispy_bootstrap5",
    "storages",
    "accounts",
    "store",
    "cart",
    "orders",
    "payments",
    "reviews",
    "marketing",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not DEBUG:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "furniture_store.urls"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.cart_context",
                "core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "furniture_store.wsgi.application"

DATABASE_URL = config("DATABASE_URL", default="")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DB_NAME = config("DB_NAME", default="")
    DB_USER = config("DB_USER", default="")
    DB_PASSWORD = config("DB_PASSWORD", default="")
    DB_HOST = config("DB_HOST", default="localhost")
    DB_PORT = config("DB_PORT", default="5432")

    if DB_NAME and DB_USER:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": DB_NAME,
                "USER": DB_USER,
                "PASSWORD": DB_PASSWORD,
                "HOST": DB_HOST,
                "PORT": DB_PORT,
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
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


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

USE_AWS = config('USE_AWS', default=False, cast=bool)

import sys
print(f"[SETTINGS] USE_AWS = {USE_AWS}", file=sys.stderr)

if USE_AWS:
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")

    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME]):
        print(f"[SETTINGS] WARNING: USE_AWS=True but AWS credentials are missing!", file=sys.stderr)
        print(f"[SETTINGS]   AWS_ACCESS_KEY_ID: {'set' if AWS_ACCESS_KEY_ID else 'MISSING'}", file=sys.stderr)
        print(f"[SETTINGS]   AWS_SECRET_ACCESS_KEY: {'set' if AWS_SECRET_ACCESS_KEY else 'MISSING'}", file=sys.stderr)
        print(f"[SETTINGS]   AWS_STORAGE_BUCKET_NAME: {'set' if AWS_STORAGE_BUCKET_NAME else 'MISSING'}", file=sys.stderr)
        print(f"[SETTINGS] Falling back to local FileSystemStorage!", file=sys.stderr)
        USE_AWS = False
    raw_location = config("AWS_LOCATION", default="media")
    normalized_location = raw_location.strip().strip("/") if raw_location else "media"
    if normalized_location.startswith("app/"):
        normalized_location = normalized_location[4:]
    AWS_LOCATION = normalized_location or "media"
    region_config = config("AWS_S3_REGION_NAME", default="")
    AWS_S3_REGION_NAME = region_config.split()[-1] if region_config else ""
    if AWS_S3_REGION_NAME:
        AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
    else:
        AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }

    STORAGES = {
        "default": {
            "BACKEND": "furniture_store.storage.MediaStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    DEFAULT_FILE_STORAGE = "furniture_store.storage.MediaStorage"

    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
    MEDIA_ROOT = BASE_DIR / "media"

    print(f"[SETTINGS] S3 Storage configured successfully!", file=sys.stderr)
    print(f"[SETTINGS]   Bucket: {AWS_STORAGE_BUCKET_NAME}", file=sys.stderr)
    print(f"[SETTINGS]   Region: {AWS_S3_REGION_NAME}", file=sys.stderr)
    print(f"[SETTINGS]   Location: {AWS_LOCATION}", file=sys.stderr)
    print(f"[SETTINGS]   STORAGES[default]: {STORAGES['default']['BACKEND']}", file=sys.stderr)

    STATIC_URL = "/static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]

    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True

if not USE_AWS:
    STATIC_URL = "/static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    print(f"[SETTINGS] Using local FileSystemStorage for media files", file=sys.stderr)
    print(f"[SETTINGS]   MEDIA_URL: {MEDIA_URL}", file=sys.stderr)
    print(f"[SETTINGS]   MEDIA_ROOT: {MEDIA_ROOT}", file=sys.stderr)
    print(f"[SETTINGS]   STORAGES[default]: {STORAGES['default']['BACKEND']}", file=sys.stderr)

    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@furniturestore.com")

SITE_URL = config("SITE_URL", default="http://localhost:8000")
SITE_ID = config("SITE_ID", default=1, cast=int)
_parsed_site_url = urlparse(SITE_URL)
ACCOUNT_DEFAULT_HTTP_PROTOCOL = _parsed_site_url.scheme or ("https" if not DEBUG else "http")

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = config(
    "ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS", default=1, cast=int
)
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_ADAPTER = "accounts.adapters.CustomAccountAdapter"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Furniture Store] "

STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = True

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "furniture_store.storage": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "store.models": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
