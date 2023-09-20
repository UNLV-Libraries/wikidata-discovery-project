"""
Django settings for wikidataDiscovery project.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os
import mimetypes
from .keytrieve import get_django_key

# App-specific values
APP_VERSION = 'dev.18.8 (scheduler debug)'
APP_AUTHOR = 'Andre Hulet'
APP_EMAIL = 'andre.hulet@unlv.edu'
APP_CONTACT = 'Darnelle Melvin'
APP_CONTACT_EMAIL = 'darnelle.melvin@unlv.edu'
SPARQL_USER_AGENT_ID = 'WikiframeApp/0.9 (https://github.com/aehulet; andre.hulet@unlv.edu)'

# DO NOT DEPLOY TO PRODUCTION with DEBUG = True!
DEBUG = True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = get_django_key()  # application-specific function to retrieve encrypted key value

ALLOWED_HOSTS = ['localhost', 'ore.library.unlv.edu', 'wikiframe.library.unlv.edu',
                 'oreback.library.unlv.edu', 'oredev.library.unlv.edu', 'localwikiframe',
                 'wikiback.library.unlv.edu', 'wikidev.library.unlv.edu']

# CSRF SETTINGS to support valid cross-site requests from the rev. proxy servers: wikiframe, wikiback, wikidev
CSRF_TRUSTED_ORIGINS = ['https://wikiframe.library.unlv.edu',
                        'https://wikiback.library.unlv.edu',
                        'https://wikidev.library.unlv.edu']

# Establish MIME types
mimetypes.add_type('text/javascript', '.js', True)
mimetypes.add_type('text/css', '.css', True)

# Application definitions
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'discover.apps.DiscoverConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wikidataDiscovery.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'wikidataDiscovery.wsgi.application'
DJANGO_SETTINGS_MODULE = 'wikidataDiscovery.settings'

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': str(BASE_DIR / 'my.cnf')
        }
    }
}
# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_TZ = True

# SESSION SETTINGS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = 'Lax'
# SESSION_COOKIE_AGE = 604800  # 7 days, in seconds

# STATIC FILES (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = '/data/www/wd_static/'

STATICFILES_DIRS = [
    str(BASE_DIR / 'discover/static/discover'),
    str(BASE_DIR / 'discover/static/external'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "issue.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "discover.wd_utils": {
          "handlers": ["file"],
          "level": "ERROR",
          "propagate": True,
        },
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {module} {process:d} {message}",
            "style": "{",
        }
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


