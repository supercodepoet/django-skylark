import os
from random import sample
import string

from django.conf import settings as django_settings
from urlparse import urljoin


# General settings
if hasattr(django_settings, 'STATIC_ROOT'):
    SKYLARK_CACHE_ROOT = os.path.join(django_settings.STATIC_ROOT, 'cfcache')
    SKYLARK_CACHE_URL = urljoin(django_settings.STATIC_URL, 'cfcache/')

else:
    SKYLARK_CACHE_ROOT = os.path.join(django_settings.MEDIA_ROOT, 'cfcache')
    SKYLARK_CACHE_URL = urljoin(django_settings.MEDIA_URL, 'cfcache/')

SKYLARK_INIT_CLEAR_CACHE = False
SKYLARK_PLANS = 'mediadeploy'
SKYLARK_PLANS_DEFAULT = 'default'
SKYLARK_PLANS_ROLLUP_SALT = ''.join(sample(string.hexdigits, 16))
SKYLARK_ENABLE_TIDY = False   # For now until tidylib catches up with html5
SKYLARK_RAISE_CSS_ERRORS = django_settings.DEBUG
SKYLARK_RAISE_HTML_ERRORS = django_settings.DEBUG

# Dojo toolkit related
SKYLARK_DOJO_DEBUGATALLCOSTS = django_settings.DEBUG
SKYLARK_DOJO_COPY_INTERNALBUILD = True
SKYLARK_DOJO_VIA_INTERNALBUILD = True
SKYLARK_DOJO_VIA_CDN_AOL = None
SKYLARK_DOJO_VIA_URL = None

# Chirp testing and MVC
SKYLARK_CHIRP_INSTRUMENTED = False
