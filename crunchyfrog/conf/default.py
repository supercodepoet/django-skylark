import os
from django.conf import settings as django_settings
from urlparse import urljoin

MEDIA_ROOT = django_settings.MEDIA_ROOT
MEDIA_URL  = django_settings.MEDIA_URL
CRUNCHYFROG_CACHE_ROOT = os.path.join(MEDIA_ROOT, 'cfcache')
CRUNCHYFROG_CACHE_URL  = urljoin(MEDIA_URL, 'cfcache/')
