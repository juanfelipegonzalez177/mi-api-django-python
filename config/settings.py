import sys
from pathlib import Path
from decouple import config

try:
    import drf_yasg  # noqa: F401
    HAS_DRF_YASG = True
except ImportError:
    HAS_DRF_YASG = False

try:
    import drf_spectacular  # noqa: F401
    HAS_DRF_SPECTACULAR = True
except ImportError:
    HAS_DRF_SPECTACULAR = False

BASE_DIR = Path(__file__).resolve().parent.parent
IS_TESTING = 'test' in sys.argv

SECRET_KEY = config('SECRET_KEY', default='django-insecure-local-dev-key')
JWT_SECRET = config('JWT_SECRET', default=SECRET_KEY)
JWT_EXP_MINUTES = config('JWT_EXP_MINUTES', default=120, cast=int)
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'domain',
    'infrastructure',
    'application',
    'api',
]

if HAS_DRF_YASG:
    INSTALLED_APPS.append('drf_yasg')

if HAS_DRF_SPECTACULAR:
    INSTALLED_APPS.append('drf_spectacular')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.middlewares.error_middleware.GlobalExceptionMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

if IS_TESTING:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    db_engine = config('DB_ENGINE', default='django.db.backends.sqlite3')
    DATABASES = {
        'default': {
            'ENGINE': db_engine,
            'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
            'USER': config('DB_USER', default=''),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default=''),
            'PORT': config('DB_PORT', default=''),
            'OPTIONS': {
                'sslmode': 'require',
            } if db_engine == 'django.db.backends.postgresql' else {},
        }
    }

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [],
} if HAS_DRF_SPECTACULAR else {}

SPECTACULAR_SETTINGS = {
    'TITLE': 'API Companias y Empleados',
    'DESCRIPTION': 'API REST con Django y Onion Architecture',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayOperationId': False,
        'defaultModelsExpandDepth': -1,
        'persistAuthorization': True,
    },
    'SECURITY': [{'BearerAuth': []}],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': 'Pega solo el token JWT, sin escribir Bearer.',
            }
        }
    },
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Escribe: Bearer <tu_token>',
        }
    },
    'USE_SESSION_AUTH': False,
}

LOGGING_HANDLERS = ['console'] if IS_TESTING else ['console', 'file']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} — {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': LOGGING_HANDLERS,
        'level': 'INFO',
    },
}
