"""
Django settings for E_learning project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
""" 
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
# import django_heroku

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =True   
if DEBUG == False:
    TEMPLATE_DEBUG = DEBUG
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SECURE_SSL_REDIRECT=True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000 #year
    SECURE_HSTS_PRELOAD =True
    SESSION_COOKIE_PATH = '/;HttpOnly'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    CSRF_COOKIE_SECURE = True 
    SECURE_REFERRER_POLICY = 'same-origin'
    SECURE_HSTS_INCLUDE_SUBDOMAINS =True
# ALLOWED_HOSTS = ["127.0.0.1","www.agartha.academy","agartha.academy"]
ALLOWED_HOSTS = ["localhost",'kemet.localhost',"127.0.0.1","kemet.127.0.0.1"]
  
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #y apps
    "home", 
    "Quiz",
    "accounts.apps.AccountsConfig",
    "Blogs",
    "Consultant",
    "Dashboard",
    "Frontend",
    "library",
    #my packegs
    "django_hosts",
    'rosetta',
    'embed_video',
    "taggit",
    'ckeditor',
    'ckeditor_uploader',
    'crispy_forms',
    'allauth',         
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',    
    'allauth.socialaccount.providers.linkedin_oauth2',    
    'bootstrap_datepicker_plus',
    "tempus_dominus",

    'django_cleanup',
    'captcha',
    "admin_honeypot",
    "modeltranslation",
  'phonenumber_field',
] 

MIDDLEWARE = [
    "django_hosts.middleware.HostsRequestMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.OneSessionPerUserMiddleware',
    'crum.CurrentRequestUserMiddleware',
    "django_hosts.middleware.HostsResponseMiddleware"
       ]

ROOT_URLCONF = 'E_learning.urls'
ROOT_HOSTCONF = 'E_learning.hosts'
DEFAULT_HOST ="www"  
# APPEND_SLASH=False 
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/"templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "home.processors.global_wishlist",
                "home.processors.global_news",

                

            ],
        },
    },
]

WSGI_APPLICATION = 'E_learning.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


# DATABASES = {    
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR ,'db.sqlite3'),
#     }
# }    
  
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
DATABASES={   
    "default":{
        "ENGINE":"django.db.backends.mysql",
        "NAME":"agarthaa_e_learning",
        "USER":"agarthaa_root",
        "PASSWORD":"AgarthaNew",
        "HOST":"localhost",
        "PORT":"3307",
        'OPTIONS':{'sql_mode': 'STRICT_ALL_TABLES'},
    }      
}  
CACHES = { 
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}
#debug toolbar
# INTERNAL_IPS = [
   
#     "127.0.0.1",
   
# ]
# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL ="accounts.User"
# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = 'en-us'
LANGUAGES = (            # supported languages
    ('en', _('English')),
    ("ar",_("Arabic")),
)
TIME_ZONE = 'Africa/Cairo'
TEMPUS_DOMINUS_LOCALIZE=True 

MODELTRANSLATION_LANGUAGES = ['en',"ar"]

STATIC_URL = '/static/'
STATIC_ROOT=BASE_DIR/"static"
STATICFILES_DIRS=[
  BASE_DIR/"static_in_env"

]  
     
# for translation
USE_I18N = True
USE_L10N = True
LOCALE_PATHS=(   
    os.path.join(BASE_DIR,"locale/"),
             )
    
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

#date time picker
BOOTSTRAP4 = {
    'include_jquery': True,
}
# crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}
# "Email Backend"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtppro.zoho.com'
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD =os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = False
EMAIL_USE_SSL= True
EMAIL_PORT = 465 
#allauth   
SITE_ID=1 
LOGIN_REDIRECT_URL ="home:home"
LOGIN_URL = 'account_login'
LOGOUT_URL = 'account_logout'
# ACCOUNT_ADAPTER="accounts.adapter.MyLoginAccountAdapter"
SOCIALACCOUNT_ADAPTER ="accounts.adapter.MySocialAccountAdapter"
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS =True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL=LOGIN_REDIRECT_URL
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL =None
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS =1
ACCOUNT_EMAIL_CONFIRMATION_HMAC =True
ACCOUNT_EMAIL_REQUIRED =True
ACCOUNT_EMAIL_VERIFICATION ="mandatory"   
ACCOUNT_EMAIL_SUBJECT_PREFIX ="Site"
ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN =120
ACCOUNT_EMAIL_MAX_LENGTH=245
ACCOUNT_MAX_EMAIL_ADDRESSES=1
ACCOUNT_LOGIN_ATTEMPTS_LIMIT =3
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT =120
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION =True
ACCOUNT_LOGOUT_ON_GET =True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE =True
ACCOUNT_LOGIN_ON_PASSWORD_RESET =True
ACCOUNT_LOGOUT_REDIRECT_URL ="home:home"
ACCOUNT_PASSWORD_INPUT_RENDER_VALUE =True
ACCOUNT_PRESERVE_USERNAME_CASING =True
ACCOUNT_SESSION_REMEMBER =False
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
SESSION_COOKIE_AGE =  20 * 60
SESSION_SAVE_EVERY_REQUEST = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE =True
ACCOUNT_SIGNUP_REDIRECT_URL =LOGIN_REDIRECT_URL
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# ACCOUNT_USERNAME_BLACKLIST (=[])
ACCOUNT_UNIQUE_EMAIL =True
ACCOUNT_USERNAME_MIN_LENGTH =3
ACCOUNT_USERNAME_REQUIRED =True 
SOCIALACCOUNT_AUTO_SIGNUP =True
SOCIALACCOUNT_EMAIL_VERIFICATION =True
SOCIALACCOUNT_EMAIL_REQUIRED =True
SOCIALACCOUNT_QUERY_EMAIL =True
SOCIALACCOUNT_STORE_TOKENS =True
ACCOUNT_DEFAULT_HTTP_PROTOCOL='https'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
        'client_id':os.environ["google_client_id"],
        'secret':os.environ["google_secret"],
        'key': '',  
        'SCOPE': [
            'profile',
            'email',
        ],
    'VERIFIED_EMAIL': True,
       
    }
    },
       'facebook': {
    'APP': {
        'client_id':os.environ["facebook_client_id"],
        'secret':os.environ["facebook_secret"],
        'key': '',
        'SCOPE': ['email', 'public_profile'],
           'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
          "email"
        ],   
         'VERIFIED_EMAIL': True,
        'VERSION': 'v7.0',
    }
    }, 
    'linkedin_oauth2': {    
    # 'SCOPE': [
    #     'r_basicprofile',
    #     # 'r_emailaddress'
    # ],
    # 'PROFILE_FIELDS': [
    #     'id',
    #     'first-name',
    #     'last-name',
    #     'email-address',
    #     'picture-url',
    #     'public-profile-url',
    # ], 
 'APP': {
        'client_id':os.environ["linkedin_client_id"],
        'secret':os.environ["linkedin_secret"],
        'key': '',
       
    },    

}
    
} 
ACCOUNT_FORMS = {
    'signup': 'accounts.forms.MyCustomSignupForm',
    'login': 'accounts.forms.MyCustomLoginForm',

} 
SOCIALACCOUNT_FORMS = {
    # 'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
    'signup': 'accounts.forms.MyCustomSocialSignupForm',
}

# python social auth
AUTHENTICATION_BACKENDS = [

#
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    #      ...
]

COURSE_MODEL="home.Course"

# CkEditor
CKEDITOR_CONFIGS = {
    'awesome_ckeditor': {
          
        
},
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': "auto",
        "language":"ar",
        'extraPlugins': ','.join([
            "language"
        ]),
},

}

CKEDITOR_UPLOAD_PATH = "ckeditor/"
CKEDITOR_IMAGE_BACKEND ="pillow"
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_RESTRICT_BY_USER =True
CKEDITOR_BROWSE_SHOW_DIRS =False
CKEDITOR_FORCE_JPEG_COMPRESSION =True
### google recaptcha
RECAPTCHA_PUBLIC_KEY = os.environ["RECAPTCHA_PUBLIC_KEY"]
RECAPTCHA_PRIVATE_KEY = os.environ["RECAPTCHA_PRIVATE_KEY"]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
