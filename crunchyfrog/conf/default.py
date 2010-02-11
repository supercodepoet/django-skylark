import os
from django.conf import settings as django_settings
from urlparse import urljoin

# General settings
CRUNCHYFROG_CACHE_ROOT = os.path.join(django_settings.MEDIA_ROOT, 'cfcache')
CRUNCHYFROG_CACHE_URL = urljoin(django_settings.MEDIA_URL, 'cfcache/')
CRUNCHYFROG_INIT_CLEAR_CACHE = False
CRUNCHYFROG_PLANS = 'mediadeploy'
CRUNCHYFROG_PLANS_DEFAULT = 'default'
CRUNCHYFROG_ENABLE_TIDY = True
CRUNCHYFROG_RAISE_CSS_ERRORS = django_settings.DEBUG
CRUNCHYFROG_RAISE_HTML_ERRORS = django_settings.DEBUG

# Dojo toolkit related
CRUNCHYFROG_DOJO_DEBUGATALLCOSTS = django_settings.DEBUG
CRUNCHYFROG_DOJO_COPY_INTERNALBUILD = True
CRUNCHYFROG_DOJO_VIA_INTERNALBUILD = True
CRUNCHYFROG_DOJO_VIA_CDN_AOL = None
CRUNCHYFROG_DOJO_VIA_URL = None
CRUNCHYFROG_DOJO_VIA_PATH = None

# Ribt testing and MVC
CRUNCHYFROG_RIBT_INSTRUMENTED = False
