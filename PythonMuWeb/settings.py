from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--@u@^g+0=xg&5)cnywirca@ax8x_fe2&ki8wl*o^k!($v92-=2'

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
    'Site',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Site.middlewares.themeMiddleware',
]

ROOT_URLCONF = 'PythonMuWeb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Diretório onde os templates estão
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'Site.context_processors.global_theme',
                'Site.context_processors.get_total_online',
                'Site.context_processors.site_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'PythonMuWeb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'PyMuWeb',  # Banco de dados para o site
        'USER': 'sa',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Encrypt': 'yes',
            'TrustServerCertificate': 'yes',
        },
    },
    'muonline': {
        'ENGINE': 'mssql',
        'NAME': 'MuOnlineS6',  # Banco de dados do jogo
        'USER': 'sa',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'Encrypt': 'yes',
            'TrustServerCertificate': 'yes',
        },
    }
}

DATABASE_ROUTERS = ['Site.routers.MultiDBRouter']


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        },
    },
    #{
    #    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    #},
    #{
    #    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    #},
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Configuração de arquivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / "Site" / "templates",  # O Django vai procurar os arquivos estáticos em 'Site/templates'
]
STATIC_URL = '/static/'  # URL base para acessar os arquivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Configuração para arquivos carregados pelo usuário (não estáticos)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Diretório para arquivos carregados pelo usuário
MEDIA_URL = '/media/'  # URL base para acessar os arquivos carregado

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
