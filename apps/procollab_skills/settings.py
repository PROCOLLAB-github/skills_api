import mimetypes
import os
from datetime import timedelta
from pathlib import Path

from decouple import config
from yookassa import Configuration

mimetypes.add_type("application/javascript", ".js", True)
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/html", ".html", True)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY", cast=str, default="some_key")

DEBUG = config("DEBUG", cast=bool, default=False)

# ALLOWED_HOSTS = [
#     "127.0.0.1:8001",
#     "127.0.0.1:8000",
#     "127.0.0.1",
#     "localhost",
#     "0.0.0.0",
#     "api.skills.procollab.ru",
#     "skills.procollab.ru",
#     "app.procollab.ru",
#     "procollab.ru",
#     "skills.dev.procollab.ru",
#     "skills.prod.procollab.ru",
#     "web",  # From Docker
#     "5.188.81.217",
#     "5.188.81.217:8001"
#     "skills_web"
# ]
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://0.0.0.0:8000",
    "https://api.procollab.ru",
    "https://procollab.ru",
    "https://www.procollab.ru",
    "https://app.procollab.ru",
    "https://dev.procollab.ru",
    "https://skills.dev.procollab.ru",
    "http://45.131.98.58:8001",
    "https://api.skills.procollab.ru",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",  # required for Django collectstatic discovery
    "celery",
    "django_celery_beat",
    "corsheaders",
    # plugins
    "django_summernote",
    # apps
    "courses",
    "files",
    "progress",
    "questions",
    "subscription",
    "webinars",
    "trajectories",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "procollab_skills.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR, "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "procollab_skills.wsgi.application"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "procollab_skills.auth.CustomAuth",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://skills_redis:6379/0",
    }
}

AUTH_USER_MODEL = "progress.CustomUser"

# настройки SELECTEL
DEFAULT_FILE_STORAGE = "django_selectel_storage.storage.SelectelStorage"

SELECTEL_ACCOUNT_ID = config("SELECTEL_ACCOUNT_ID", cast=str, default="123456")
SELECTEL_CONTAINER_NAME = config("SELECTEL_CONTAINER_NAME", cast=str, default="asdd")
SELECTEL_SERVICE_USERNAME = config("SELECTEL_SERVICE_USERNAME", cast=str, default="PWD")
SELECTEL_SERVICE_PASSWORD = config("SELECTEL_SERVICE_PASSWORD", cast=str, default="PWD")
SELECTEL_PROJECT_NAME = config("SELECTEL_PROJECT_NAME", cast=str, default="PWD")
SELECTEL_READ_FILES_DOMAIN = config("SELECTEL_READ_FILES_DOMAIN", cast=str, default="PWD")
SELECTEL_PROJECT_ID = config("SELECTEL_PROJECT_ID", cast=str, default="PWD")

SELECTEL_NEW_AUTH_TOKEN = "https://cloud.api.selcloud.ru/identity/v3/auth/tokens"
SELECTEL_UPLOAD_URL = f"https://swift.ru-1.storage.selcloud.ru/v1/{SELECTEL_PROJECT_ID}/{SELECTEL_CONTAINER_NAME}/"


SUMMERNOTE_CONFIG = {
    #  'attachment_upload_to':lambda x: None,
    "disable_attachment": False,
}
SELECTEL_STORAGES = {
    "default": {
        "USERNAME": SELECTEL_SERVICE_USERNAME,
        "PASSWORD": SELECTEL_SERVICE_PASSWORD,
        "CONTAINER_NAME": SELECTEL_CONTAINER_NAME,
    },
}

# Костыль для тестов в workflow и локальной отладки
USE_SQLITE: bool = config("USE_SQLITE", cast=bool, default=False)

if USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DATABASE_NAME", default="postgres", cast=str),
            "USER": config("DATABASE_USER", default="postgres", cast=str),
            "PASSWORD": config("DATABASE_PASSWORD", default="postgres", cast=str),
            "HOST": config("DATABASE_HOST", default="skills_db", cast=str),
            "PORT": config("DATABASE_PORT", default="5432", cast=str),
        }
    }

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]


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


LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SPECTACULAR_SETTINGS = {
    "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVE_AUTHENTICATION": ["rest_framework.authentication.SessionAuthentication", "procollab_skills.auth.CustomAuth"],
    # OTHER SETTINGS
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    },
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
    },
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": True,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.\
default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "progress.serializers.CustomObtainPairSerializer",
}

if DEBUG:
    SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(weeks=2)

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BROKER_URL = "redis://skills_redis:6379/0"

CELERY_RESULT_BACKEND = "redis://skills_redis:6379"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"


Configuration.secret_key = config("YOOKASSA_API_KEY", default="")
Configuration.account_id = config("YOOKASSA_SHOP_ID", default="")


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


EMAIL_BACKEND = "anymail.backends.unisender_go.EmailBackend"
UNISENDER_GO_API_KEY = config("UNISENDER_GO_API_KEY", default="", cast=str)
ANYMAIL = {
    "UNISENDER_GO_API_KEY": UNISENDER_GO_API_KEY,
    "UNISENDER_GO_API_URL": "https://go1.unisender.ru/ru/transactional/api/v1/",
    "UNISENDER_GO_SEND_DEFAULTS": {
        "esp_extra": {
            "global_language": "ru",
        }
    },
}
EMAIL_USE_TLS = True
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USER = config("EMAIL_USER", cast=str, default="example@mail.ru")
