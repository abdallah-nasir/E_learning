"""
Django settings for E_learning project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
# import django_heroku

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gq)0=tf4ty9d(r=cygqos=o+a0x=d^e&f4hmg=@fooo)6uq4=c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1","188.166.152.244","www.agartha.academy","agartha.academy"]


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
    #my packegs
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
    # "allauth.socialaccount.providers.linkedin", 
    'allauth.socialaccount.providers.linkedin_oauth2',    
    'bootstrap_datepicker_plus',
    'django_cleanup',
    # "storages",   
    # "debug_toolbar",
] 

MIDDLEWARE = [
    
    'django.middleware.security.SecurityMiddleware',
   
    'django.middleware.locale.LocaleMiddleware',
       'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
    'accounts.middleware.OneSessionPerUserMiddleware',
    'crum.CurrentRequestUserMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
       ]



ROOT_URLCONF = 'E_learning.urls'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# DATABASES={
#     "default":{
#         "ENGINE":"django.db.backends.postgresql_psycopg2",
#         "NAME":"defaultdb",
#         "USER":"doadmin",
#         "PASSWORD":"KZgXyyf1suqKHVq2",
#         "HOST":"db-postgresql-lon1-26713-do-user-10425555-0.b.db.ondigitalocean.com",
#         "PORT":"25060",
#         'OPTIONS': {'sslmode': 'require'},
#     }      
# } 
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
STATIC_URL = 'https://agartha2.b-cdn.net/static/'
# MEDIA_URL="https://agartha2.b-cdn.net/static/"
# MEDIA_ROOT="https://agartha2.b-cdn.net""
STATIC_ROOT="https://agartha2.b-cdn.net"
STATICFILES_DIRS=[
  "https://agartha2.b-cdn.net/static"
]  
    
# STATIC_URL = '/static/'
# # MEDIA_URL="https://agartha2.b-cdn.net/static/"
# # MEDIA_ROOT="https://agartha2.b-cdn.net""
# STATIC_ROOT=BASE_DIR/"static"
# STATICFILES_DIRS=[
#   BASE_DIR/"static_in_env"
# ]     
# for translation
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
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'abdullahnasser6@gmail.com'
EMAIL_HOST_PASSWORD ="bbvpxmxneyglgqzt"
EMAIL_USE_TLS = True
EMAIL_USE_SSL= False
EMAIL_PORT = '587' 
#allauth   
SITE_ID=1
LOGIN_REDIRECT_URL ="home:home"
ACCOUNT_ADAPTER="allauth.account.adapter.DefaultAccountAdapter"
SOCIALACCOUNT_ADAPTER ="allauth.socialaccount.adapter.DefaultSocialAccountAdapter"
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
ACCOUNT_PRESERVE_USERNAME_CASING =False
ACCOUNT_SESSION_REMEMBER =None
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE =True
ACCOUNT_SIGNUP_REDIRECT_URL =LOGIN_REDIRECT_URL
# ACCOUNT_USERNAME_BLACKLIST (=[])
ACCOUNT_UNIQUE_EMAIL =True
ACCOUNT_USERNAME_MIN_LENGTH =3
ACCOUNT_USERNAME_REQUIRED =True
SOCIALACCOUNT_AUTO_SIGNUP =False
SOCIALACCOUNT_EMAIL_VERIFICATION =ACCOUNT_EMAIL_VERIFICATION
SOCIALACCOUNT_EMAIL_REQUIRED =ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_QUERY_EMAIL =ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_STORE_TOKENS =True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
        'client_id':"919138982949-ftjb5mrn6llc1s3bdnpias3peenncjes.apps.googleusercontent.com",
        'secret':"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",
        'key': '',
       
    }
    },
       'facebook': {
    'APP': {
        'client_id':"1088677928331903",
        'secret':"e6107d02b02adff2a13f892ae9ec3296",
        'key': '',
       
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
        'client_id':"866roqo1m80lvo",
        'secret':"3I81H1GWVbhr6nXV",
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
AUTHENTICATION_BACKENDS = [
    # ............
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    #      ...
]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



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
COURSE_MODEL="home.Course"
