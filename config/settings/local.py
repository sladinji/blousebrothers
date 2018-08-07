# -*- coding: utf-8 -*-
"""
Local settings

- Run in Debug mode
- Use console backend for emails
- Add Django Debug Toolbar
- Add django-extensions as app
"""

from .common import *  # noqa
import socket
import os
import sys

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='#0h3&2va9bi)1!==u115g5%t8#_o!i_n%0oxgky0)=g-yn2jvv')

# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['futur.blousebrothers.fr', '0.0.0.0'])

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INSTALLED_APPS += ('debug_toolbar', )

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', '172.18.0.8', '0.0.0.0', '212.234.238.49']
# tricks to have debug toolbar when developing with docker
if os.environ.get('USE_DOCKER') == 'yes':
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1]+"1"]

DEBUG_TOOLBAR_CONFIG = {
#    'SHOW_TOOLBAR_CALLBACK': lambda r: False,  # COMMENT THIS LINE TO ENABLE TOOLBAR
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ('django_extensions', )

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Your local stuff: Below this line define 3rd party library settings
STRIPE_SECRET_KEY = "sk_test_2KQKtb6qy1MPyReB6Kr3petm"
STRIPE_PUBLISHABLE_KEY = "pk_test_UbddRFpfPbpdIZqor6NZY5Zc"
STRIPE_CURRENCY = "EUR"
# Var used by dj-stripe
STRIPE_TEST_PUBLIC_KEY = STRIPE_PUBLISHABLE_KEY
STRIPE_TEST_SECRET_KEY = STRIPE_SECRET_KEY
STRIPE_LIVE_MODE = False


MANGOPAY_DEBUG_MODE = True
MANGOPAY_BASE_URL = "https://api.sandbox.mangopay.com"
MANGOPAY_PASSPHRASE = "op38EBPRsdSkU0rbPuduaoU0Ny7vegjo5TEPsv6bEdApDLShFT"

PAYPAL_API_USERNAME = 'julien-facilitator_api1.blousebrothers.fr'
PAYPAL_API_PASSWORD = '3RFTB3NFMVG7KJYP'
PAYPAL_API_SIGNATURE = 'AFcWxV21C7fd0v3bYYYRCpSSRl31APT1rdUDeTom6WERLbb3tqVk8Pte'

NOTEBOOK_ARGUMENTS = [
        # exposes IP and port
        '--ip=0.0.0.0',
        '--port=8888',
        # disables the browser
        '--no-browser',
]

# STORAGE CONFIGURATION
# ------------------------------------------------------------------------------
# Uploaded Media Files
# ------------------------
# See: http://django-storages.readthedocs.io/en/latest/index.html
INSTALLED_APPS += (
    'storages',
)

AWS_ACCESS_KEY_ID = env('DJANGO_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('DJANGO_AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME')
AWS_AUTO_CREATE_BUCKET = False
AWS_QUERYSTRING_AUTH = False
AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()

# AWS cache settings, don't change unless you know what you're doing:
AWS_EXPIRY = 60 * 60 * 24 * 7

# TODO See: https://github.com/jschneier/django-storages/issues/47
# Revert the following and use str after the above-mentioned bug is fixed in
# either django-storage-redux or boto
AWS_HEADERS = {
    'Cache-Control': six.b('max-age=%d, s-maxage=%d, must-revalidate' % (
        AWS_EXPIRY, AWS_EXPIRY))
}

#  See:http://stackoverflow.com/questions/10390244/
from storages.backends.s3boto import S3BotoStorage  #noqa
StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')  #noqa
MediaRootS3BotoStorage = lambda: S3BotoStorage(location='media')  #noqa
DEFAULT_FILE_STORAGE = 'config.settings.local.MediaRootS3BotoStorage'
# URL that handles the media served from MEDIA_ROOT, used for managing
# stored files.
MEDIA_URL = 'https://s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME


# Static Assets
# ------------------------
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE


# EMAIL
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL',
                         default='blousebrothers <noreply@blousebrothers.fr>')
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[blousebrothers] ')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# Anymail with Mailgun
INSTALLED_APPS += ("anymail", )
ANYMAIL = {
    "MAILGUN_API_KEY": 'key-0cb37ccb0c2de16fc921df70228346bc',
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
