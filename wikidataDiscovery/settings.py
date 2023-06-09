"""
Django settings for wikidataDiscovery project.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os
from .keytrieve import get_django_key

# App-specific values
APP_VERSION = 'dev.16'
APP_AUTHOR = 'Andre Hulet'
APP_EMAIL = 'andre.hulet@unlv.edu'
APP_CONTACT = 'Darnelle Melvin'
APP_CONTACT_EMAIL = 'darnelle.melvin@unlv.edu'
SPARQL_USER_AGENT_ID = 'WikiframeApp/0.9 (https://linkedin.com/andre_hulet; andre.hulet@unlv.edu)'

# DO NOT DEPLOY TO PRODUCTION with DEBUG = True!
DEBUG = False

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = get_django_key()

ALLOWED_HOSTS = ['127.0.1.1', 'localhost', 'ore.library.unlv.edu', 'wikiframe.library.unlv.edu']


# Application definition
INSTALLED_APPS = [
    'discover.apps.DiscoverConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
        'DIRS': [BASE_DIR / 'templates']
        ,
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
# SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATIC_ROOT = '/data/www/wd_static/'

STATICFILES_DIRS = [
    '/home/ed/PycharmProjects/wikidataDiscovery/discover/static/discover/',
    '/home/ed/PycharmProjects/wikidataDiscovery/node_modules/vis-network/standalone/umd/',
    '/home/ed/PycharmProjects/wikidataDiscovery/node_modules/vis-network/dist/dist/',
    '/home/ed/PycharmProjects/wikidataDiscovery/node_modules/underscore/',
    '/home/ed/PycharmProjects/wikidataDiscovery/node_modules/jquery/dist',
    '/home/ed/PycharmProjects/wikidataDiscovery/node_modules/chart.js/dist',
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
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

