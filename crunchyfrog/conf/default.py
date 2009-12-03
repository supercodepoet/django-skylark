import os
from django.conf import settings as django_settings
from urlparse import urljoin

CRUNCHYFROG_RAISE_CSS_ERRORS = django_settings.DEBUG
CRUNCHYFROG_RAISE_HTML_ERRORS = django_settings.DEBUG
CRUNCHYFROG_PLANS = 'mediadeploy'
CRUNCHYFROG_PLANS_DEFAULT = 'default'
CRUNCHYFROG_PAGEASSEMBLY_CACHE_EXPIRE = 86400
CRUNCHYFROG_ENABLE_TIDY = True
CRUNCHYFROG_CACHE_ROOT = os.path.join(django_settings.MEDIA_ROOT, 'cfcache')
CRUNCHYFROG_CACHE_URL = urljoin(django_settings.MEDIA_URL, 'cfcache/')
