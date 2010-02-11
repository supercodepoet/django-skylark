import os
import shutil

from django import http, template
from django.core.cache import cache
from django.conf import UserSettingsHolder
from crunchyfrog.conf import settings

__all__ = ['clear_media_cache', 'HttpResponse', 'RequestContext']

class HttpResponse(http.HttpResponse):
    """
    Essentially, a copy of Django's version.  We are making our own here in anticipation
    of some additional features in the future.
    """
    def __init__(self, content='', mimetype=None, status=None,
            content_type=None):
        super(HttpResponse, self).__init__(content, mimetype, status, content_type)

def copy_then_filter_settings(values, key=None):
    fs = UserSettingsHolder({})

    for name in dir(values):
        if name == name.upper() and \
           (key is None or key in name):
            value = getattr(values, name)
            setattr(fs, name, value)
    return fs

class RequestContext(template.RequestContext):
    """
    Adds the raw request to the object, we need this to perform some caching work
    later on
    """
    def __init__(self, request, dict=None, processors=None):
        from django.conf import settings as django_settings
        super(RequestContext, self).__init__(request, dict, processors)
        cf_internals = {
            'request': request,
            'settings': copy_then_filter_settings(
                django_settings, 'CRUNCHYFROG')
        }
        self['crunchyfrog_internals'] = cf_internals

__cache_cleared = False

def clear_media_cache():
    cachedir = settings.CRUNCHYFROG_CACHE_ROOT
    if os.path.isdir(cachedir):
        shutil.rmtree(cachedir)

if settings.CRUNCHYFROG_INIT_CLEAR_CACHE and not __cache_cleared:
    """
    When we initialize CF, let's delete the cache automatically if our settings
    tell us to
    """
    clear_media_cache()
    __cache_cleared = True

__copy_addons = False

def copy_addons():
    """
    There are dependencies that CrunchyFrog and Ribt have that we need to
    include whenever the application starts.

    Right now this is:
        * Dojo (slimmed down, custom build from ext/ribt_dojo.profile.js)

    At the moment, this is slime enough that we are recreating these directories
    everytime the app initializes.  At some point this may become unnaceptable.
    As the things we use from Dojo increases, where does it make sense to just
    use the entire Dojo release?  This may eventually get altered so that it
    downloads a release of Dojo and untars it into addon.
    """
    addondir = os.path.join(settings.CRUNCHYFROG_CACHE_ROOT, 'addon')
    if os.path.isdir(addondir):
        shutil.rmtree(addondir)
    thisdir = os.path.dirname(__file__)
    mediadir = ['templates', 'ribt', 'media',]
    dojodir = os.path.join(thisdir, *(mediadir + ['dojo']))
    shutil.copytree(dojodir, os.path.join(addondir, 'dojo'))

if settings.CRUNCHYFROG_DOJO_COPY_INTERNALBUILD and not __copy_addons:
    copy_addons()
    __copy_addons = True
