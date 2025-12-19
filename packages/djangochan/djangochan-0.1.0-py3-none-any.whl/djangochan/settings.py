import environ
import os
import secrets

env = environ.Env(
    DEBUG=(bool, False),
    CAPTCHA=(bool, False),
    API_ON=(bool, True),
    WWW_ON=(bool, True),
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKDIR = os.environ.get('DJANGOCHAN_WORKDIR', os.getcwd())

for env_path in (os.path.join(WORKDIR, '.env'), os.path.join(BASE_DIR, '.env')):
    if os.path.exists(env_path):
        env.read_env(env_path)
        break

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY', default=None)
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(50)
CAPTCHA = env('CAPTCHA')
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default="127.0.0.1 localhost").split()

SITE_ID = 1

API_ON = env('API_ON')
WWW_ON = env('WWW_ON')

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SAMESITE = 'Strict'

INSTALLED_APPS = [
    'djangochan',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'core',  # djangochan
    'precise_bbcode',
    'simplemathcaptcha',
    'siteprofile',
    'sorl.thumbnail',
]

if API_ON:
    INSTALLED_APPS += [
        'api',  # djangochan
        'rest_framework',
    ]

if WWW_ON:
    INSTALLED_APPS += [
        'boards',  # djangochan
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangochan.middleware.timezone_middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'djangochan.urls'

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
                'siteprofile.context_processors.site_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangochan.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(WORKDIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = tuple(
    p for p in (os.path.join(BASE_DIR, "staticfiles"),) if os.path.exists(p)
)
STATIC_ROOT = env('STATIC_ROOT', default=os.path.join(WORKDIR, 'static'))

MEDIA_URL = 'media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=os.path.join(WORKDIR, 'media'))

# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache set up
# https://docs.djangoproject.com/en/6.0/topics/cache/

if DEBUG or not WWW_ON:
    CACHE_BACKEND = 'django.core.cache.backends.dummy.DummyCache'
else:
    CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'

CACHES = {
    'default': {
        'BACKEND': CACHE_BACKEND,
        'LOCATION': 'djangochan-cache',
    }
}
