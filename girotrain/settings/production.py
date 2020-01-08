from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4@h0kyn$tum8_&rlrg*lyn!i@yy)f@utzwqly)ja+($kdsuz+u'

#SECURE_CONTENT_TYPE_NOSNIFF = True

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['www.buchetmann.org']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/var/www/ssd1470/priv/db.conf',
        },
    }
}

STATIC_ROOT = '/var/www/ssd1470/htdocs/wagtail/static/'
STATIC_URL = '/static/'

MEDIA_ROOT = '/var/www/ssd1470/htdocs/wagtail/media/'
MEDIA_URL = '/media/'


try:
    from .local import *
except ImportError:
    pass
