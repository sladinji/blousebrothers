# -*- coding: utf-8 -*-
"""
Django settings for blousebrothers project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals
from oscar.defaults import *  #noqa
from oscar import get_core_apps
from oscar import OSCAR_MAIN_TEMPLATE_DIR
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.conf import Settings as thumbnail_settings
from boto.s3.connection import OrdinaryCallingFormat  #noqa
from django.utils import six  #noqa

import environ

ROOT_DIR = environ.Path(__file__) - 3  # (blousebrothers/config/settings/common.py - 3 = blousebrothers/)
APPS_DIR = ROOT_DIR.path('blousebrothers')

env = environ.Env()

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin
    'django.contrib.admin',
    'nested_admin',
    'cookielaw',
    'tinycontent',
    'django_csv_exports',
]
THIRD_PARTY_APPS = [
    'crispy_forms',  # Form layouts
    'allauth',  # registration
    'allauth.account',  # registration
    'allauth.socialaccount',  # registration
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'django_bootstrap_dynamic_formsets',
    'bootstrap3',
    'djng',
    'django_select2',
    'django_activeurl',
    'easy_thumbnails',
    'image_cropping',
    'mangopay',
    'hijack',
    'compat',
    'hijack_admin',
    'analytical',
    'robots',  # generate robots.txt file for google
    'cuser',  # current user middleware
    'django_social_share',  # facebook twitter button
    'termsandconditions',  # CGU-CGV
    'meta',  # SEO
    'invitations',  # Sponsoring
    'localflavor',  # IbanField
    'disqus',  # Forum
    'paypal',
    'jchart',
    'django_bleach',

]

# Apps specific for this project go here.
LOCAL_APPS = [
    'blousebrothers.users',  # custom users app
    'blousebrothers.confs',  # confs app
    'blousebrothers.cards',  # revisons/fiches app
    'blousebrothers.friends',  # friends relationship, cards sharing
    # Your stuff: custom apps go here
    'widget_tweaks',
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + get_core_apps(
      ['blousebrothers.dashboard',
       'blousebrothers.catalogue',
       'blousebrothers.catalogue.reviews',
       'blousebrothers.checkout',
       'blousebrothers.basket',
       'blousebrothers.partner',
       'blousebrothers.search',
       ]
)
SITE_ID = 1
# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cuser.middleware.CuserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.locale.LocaleMiddleware',
  #  'googlebot.middleware.GooglebotMiddleware',
    'termsandconditions.middleware.TermsAndConditionsRedirectMiddleware',


)

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'blousebrothers.contrib.sites.migrations',
    # local path for migration for the termsandconditions
    'termsandconditions': 'blousebrothers.termsandconditions.migrations',
}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL',
                         default='BlouseBrothers <support@blousebrothers.fr>')
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django_mailgun.MailgunBackend')
MAILGUN_ACCESS_KEY = env('DJANGO_MAILGUN_API_KEY')
MAILGUN_SERVER_NAME = env('DJANGO_MAILGUN_SERVER_NAME')
EMAIL_SUBJECT_PREFIX = env("DJANGO_EMAIL_SUBJECT_PREFIX", default='[blousebrothers] ')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
NEW_RELIC_LICENSE_KEY = env('NEW_RELIC_LICENSE_KEY', default="")
NEW_RELIC_APP_NAME = env('NEW_RELIC_APP_NAME', default="")
MAILGUN_SENDER_DOMAIN = 'blousebrothers.fr'

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("""Julien Almarcha""", 'julien.almarcha@gmail.com'),
    ("""Guillaume Debellemanière""", 'guillaumedebel@gmail.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
    'default': env.db('DATABASE_URL', default='postgres://blousebrothers:blousebrothers@postgres:5432/blousebrothers'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'fr'
LANGUAGES = (
      ('fr', _('French')),
)
LOCALE_PATHS = (
        '/app/locale',  # replace with correct path here
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
            OSCAR_MAIN_TEMPLATE_DIR,
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
                'blousebrothers.context_processor.subscriptions',
                #  'blousebrothers.context_processor.balance',
                'blousebrothers.context_processor.invit_form',
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGOUT_ON_GET = True

ACCOUNT_ALLOW_REGISTRATION = True
ACCOUNT_ADAPTER = 'blousebrothers.users.adapters.AccountAdapter'
ADAPTER = 'blousebrothers.users.adapters.AccountAdapter'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
SOCIALACCOUNT_ADAPTER = 'blousebrothers.users.adapters.SocialAccountAdapter'

SOCIALACCOUNT_PROVIDERS = {
    'facebook':
    {'METHOD': 'oauth2',
     'SCOPE': ['email', 'public_profile', 'user_friends'],
     'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
     'FIELDS': [
         'id',
         'email',
         'name',
         'first_name',
         'last_name',
         'verified',
         'locale',
         'timezone',
         'link',
         'gender',
         'updated_time'],
     'EXCHANGE_TOKEN': True,
     'LOCALE_FUNC': lambda request: 'fr_FR',
     'VERIFIED_EMAIL': False,
     'VERSION': 'v2.6'}
}


# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = reverse_lazy('cards:home')
LOGIN_URL = 'account_login'
ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy('home')

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'


# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'

# Your common stuff: Below this line define 3rd party library settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://solr:8983/solr/mycore',
        'INCLUDE_SPELLING': True,
        'EXCLUDED_INDEXES': ['oscar.apps.search.search_indexes.ProductIndex',
                             'blousebrothers.search.search_indexes.CoreProductIndex', ],
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
OSCAR_SEARCH_FACETS = {
    'fields': OrderedDict([
        ('product_class', {'name': _('Type'), 'field': 'product_class'}),
        ('rating', {'name': _('Rating'), 'field': 'rating'}),
        ('spe', {'name': 'Spécialité', 'field': 'spe'}),
        ('conf_items', {'name': 'Items', 'field': 'conf_items'}),
    ]),
    'queries': OrderedDict([
        #    ('price_range',
        #     {
        #         'name': _('Price range'),
        #         'field': 'price',
        #         'queries': [
        #             # This is a list of (name, query) tuples where the name will
        #             # be displayed on the front-end.
        #             (_('0 to 20'), u'[0 TO 20]'),
        #             (_('20 to 40'), u'[20 TO 40]'),
        #             (_('40 to 60'), u'[40 TO 60]'),
        #             (_('60+'), u'[60 TO *]'),
        #         ]
        #     }),
    ]),
}
OSCAR_DASHBOARD_NAVIGATION.append(
    {
        'label': _('PayPal'),
        'icon': 'icon-globe',
        'children': [
            {
                'label': _('Express transactions'),
                'url_name': 'paypal-express-list',
            },
        ]
    })

OSCAR_DEFAULT_CURRENCY = 'EUR'
OSCAR_SHOP_NAME = "BlouseBrothers"
OSCAR_SHOP_TAGLINE = 'Prépa ECNi Collaborative'

OSCAR_FROM_EMAIL = 'support@blousebrothers.fr'

OSCAR_PRODUCTS_PER_PAGE = 31
OSCAR_HOMEPAGE = reverse_lazy('catalogue:index')

THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
    ) + thumbnail_settings.THUMBNAIL_PROCESSORS

MANGOPAY_CLIENT_ID = "blousebrothers"

HIJACK_ALLOW_GET_REQUESTS = True
HIJACK_REGISTER_ADMIN = False

GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-88739323-1'
GOOGLE_ANALYTICS_SITE_SPEED = True
PIWIK_DOMAIN_PATH = 'blousebrothers.piwikpro.com'
PIWIK_SITE_ID = '1'
ANALYTICAL_INTERNAL_IPS = ["109.190.133.24",
                           "109.190.222.42",
                           "109.190.238.231",
                           "176.138.173.38",
                           "178.23.38.195",
                           "213.245.242.230",
                           "213.32.77.47",
                           "37.164.62.208",
                           "37.165.35.50",
                           "82.235.89.141",
                           "212.234.238.49",
                           ]

STRIPE_CHARGE_AND_CAPTURE_IN_ONE_STEP = True

# TERMS AND CONDITIONS
TERMS_BASE_TEMPLATE = 'account/base.html'
TERMS_EXCLUDE_URL_LIST = {'/', '/terms/required/', '/logout/', '/login/', '/cgu/'}
TERMS_EXCLUDE_URL_PREFIX_LIST = {'/catfish/', '/admin/', '/dashboard'}

# SEO
META_INCLUDE_KEYWORDS = ["Entraînement aux ECN", "préparation en ligne aux ECNi",  "ecni", "iecn", "ecn", "prépa ecn",
                         "prépa ECNi", "préparation ECN", "boite de confs",
                         "dossier clinique progressif", "dossiers cliniques progressifs",
                         "question isolée", "questions isolées", "lca", "lecture critique d'articles",
                         "lecture critique d'article", "Epreuves Classantes Nationales", "examen classant national",
                         "blouse brother", "blouse brothers", "blouses brothers",
                         "conférences"]
META_SITE_PROTOCOL = 'https'
META_USE_SITES = True
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
INVITATIONS_INVITATION_EXPIRY = 30

# DISQUS
DISQUS_API_KEY = 'ZrL5cW1Ej4uUYOUx3kIjkK9T2m3lxp4mBHU5WdIG5WzqFmuCpgFfXHmo779whvLh'
DISQUS_PUBLIC_KEY = 'ZrL5cW1Ej4uUYOUx3kIjkK9T2m3lxp4mBHU5WdIG5WzqFmuCpgFfXHmo779whvLh'
DISQUS_SECRET_KEY = 'CA69jaIVIPCWKhZH353BA0sRdkn4PyhU5Yl5Xmmc1f5bvaKmQ6lnUreaJVX0BcHu'
DISQUS_WEBSITE_SHORTNAME = 'blousebrothers'

# bleach
# Which HTML tags are allowed
BLEACH_ALLOWED_TAGS = ['br', 'img', 'div', 'ul', 'li', 'font', 'color', 'span', 'p', 'b', 'i', 'u', 'em', 'strong', 'a']

# Which HTML attributes are allowed
BLEACH_ALLOWED_ATTRIBUTES = ['href', 'src', 'color', 'title', 'style']

# Which CSS properties are allowed in 'style' attributes (assuming style is
# an allowed attribute)
BLEACH_ALLOWED_STYLES = [
        'opacity', 'font-family', 'font-weight', 'font-color', 'color',  'text-decoration', 'font-variant']

# Strip unknown tags if True, replace with HTML escaped characters if False
BLEACH_STRIP_TAGS = True

# Strip HTML comments, or leave them in.
BLEACH_STRIP_COMMENTS = True
