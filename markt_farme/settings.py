# settings.py
from pathlib import Path
from dotenv import load_dotenv


import os

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Dossier des fichiers médias
MEDIA_URL = '/media/'  # URL publique pour accéder aux fichiers médias
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Dossier physique où seront stockées les images
MEDIA_ROOT = BASE_DIR / 'media'



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-wpfww5%nc3yd+_2sw08m_keep0&ph5t%ma-%q_um#uepw8bw8a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'accounts.User'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'products',
    'crispy_forms',
    'widget_tweaks',
    'crispy_bootstrap5', 
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'django_extensions',

]


CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Paramètres CORS pour autoriser les requêtes depuis un frontend séparé
CORS_ORIGIN_ALLOW_ALL = True  # Pour autoriser toutes les origines (attention en prod)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


ROOT_URLCONF = 'markt_farme.urls'

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

WSGI_APPLICATION = 'markt_farme.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
#stocker les fichiers " staticfiles " collectés dans un dossier spécifique
STATIC_ROOT = BASE_DIR / "staticfiles"
# python3 manage.py collectstatic / copie du static
 


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# LANGUAGES: Langues disponibles pour le projet
LANGUAGES = [
    ('fr', 'Français'),
    ('nl', 'Nederlands'),
    ('en', 'English'),
]

# Paramètre pour définir la langue par défaut
LANGUAGE_CODE = 'fr'  # Par défaut, la langue est le français

# Activer la gestion multilingue
USE_I18N = True

# Paramètres pour les fichiers de traduction (généralement en 'locale')
LOCALE_PATHS = [
    BASE_DIR / 'locale',  # Dossier où se trouvent vos fichiers de traduction
]

# Configuration des formats de date/heure pour chaque langue
DATE_INPUT_FORMATS = ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d']

# Configurez les fichiers médias (si nécessaire pour les images et téléchargements)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Autres configurations de Django
USE_L10N = True
USE_TZ = True


 # Config générals sécu https 
 
# Configuration des chemins des fichiers SSL
BASE_DIR = Path(__file__).resolve().parent.parent

# Rediriger tout le trafic HTTP vers HTTPS
SECURE_SSL_REDIRECT = True 
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Définir les chemins de certificat SSL
SSL_CERTIFICATE_PATH = os.path.join(BASE_DIR, 'ssl', 'cert.pem')
SSL_KEY_PATH = os.path.join(BASE_DIR, 'ssl', 'key.pem')

# Api - openstreetmap - App OAuth2 ----> généré sur : https://www.openstreetmap.org/oauth2/applications

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Clé API OpenStreetMap
# OPENSTREETMAP_OAUTH2_CLIENT_ID = os.getenv('OPENSTREETMAP_OAUTH2_CLIENT_ID')


# Clés API OpenStreetMap
OPENSTREETMAP_OAUTH2_CLIENT_ID = os.getenv('OPENSTREETMAP_OAUTH2_CLIENT_ID')
OPENSTREETMAP_OAUTH2_CLIENT_SECRET = os.getenv('OPENSTREETMAP_OAUTH2_CLIENT_SECRET')
OPENSTREETMAP_OAUTH2_REDIRECT_URI = os.getenv('OPENSTREETMAP_OAUTH2_REDIRECT_URI')

# Vérification (facultatif, pour debugger)
# print("OPENSTREETMAP_OAUTH2_CLIENT_ID:", OPENSTREETMAP_OAUTH2_CLIENT_ID)


# OPENSTREETMAP_OAUTH2_CLIENT_ID = 'T9wg_q-Ly9Y0zrpCn7Bj-ymtz9bokzxs-irIGR7Gu7Y'
# OPENSTREETMAP_OAUTH2_CLIENT_SECRET = '9q6OedRBdLV1THouTWONRNLiRRFQJsOSQpmTswW-RGE'
# OPENSTREETMAP_OAUTH2_REDIRECT_URI = 'https://127.0.0.1:8000'