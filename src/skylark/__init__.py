import os
import time
import shutil

from django import http, template
from django.conf import UserSettingsHolder

from skylark.conf import settings
from skylark import templatepatch

__all__ = ['clear_media_cache', 'time_started',
           'HttpResponse', 'RequestContext']

__time_started = time.time()


def time_started():
    return __time_started


class HttpResponse(http.HttpResponse):
    """
    Essentially, a copy of Django's version.  We are making our own here in
    anticipation of some additional features in the future.
    """
    def __init__(self, content='', mimetype=None, status=None,
        content_type=None):
        super(HttpResponse, self).__init__(
            content, mimetype, status, content_type)


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
    Adds the raw request to the object, we need this to perform some caching
    work later on
    """
    def __init__(self, request, dict=None, processors=None):
        from django.conf import settings as django_settings
        super(RequestContext, self).__init__(request, dict, processors)
        if hasattr(request, 'skylark_internals'):
            internals = request.skylark_internals
        else:
            # We want all the RequestContext created from this request to share
            # this dict
            internals = {
                'request': request,
                'assembly_stack': [],
                'settings': copy_then_filter_settings(
                    django_settings, 'SKYLARK')}
            # Hook the request object
            setattr(request, 'skylark_internals', internals)

        self['skylark_internals'] = internals

__cache_cleared = False


def clear_media_cache():
    cachedir = settings.SKYLARK_CACHE_ROOT
    # Some directories in the cache should not be deleted
    skip = ['addon']
    if not os.path.isdir(cachedir):
        return
    for topdir in os.listdir(cachedir):
        if topdir in skip:
            continue
        d = os.path.join(cachedir, topdir)
        if os.path.isdir(d):
            shutil.rmtree(d)

if settings.SKYLARK_INIT_CLEAR_CACHE and not __cache_cleared:
    """
    When we initialize CF, let's delete the cache automatically if our settings
    tell us to
    """
    clear_media_cache()
    __cache_cleared = True

__copy_addons = False


def copy_addons():
    """
    There are dependencies that Django Skylark and Chirp have that we need to
    include whenever the application starts.

    Right now this is:
        * Dojo (slimmed down, custom build from ext/chirp_dojo.profile.js)

    At the moment, this is slime enough that we are recreating these
    directories everytime the app initializes.  At some point this may become
    unnaceptable.  As the things we use from Dojo increases, where does it make
    sense to just use the entire Dojo release?  This may eventually get altered
    so that it downloads a release of Dojo and untars it into addon.
    """
    addondir = os.path.join(settings.SKYLARK_CACHE_ROOT, 'addon')
    if os.path.isdir(addondir):
        # Don't copy it again, that's silly
        return
    thisdir = os.path.dirname(__file__)
    mediadir = ['templates', 'chirp', 'media', ]
    dojodir = os.path.join(thisdir, *(mediadir + ['dojo']))
    shutil.copytree(dojodir, os.path.join(addondir, 'dojo'))
    dojoxdir = os.path.join(thisdir, *(mediadir + ['dojox']))
    shutil.copytree(dojoxdir, os.path.join(addondir, 'dojox'))

if settings.SKYLARK_DOJO_COPY_INTERNALBUILD and not __copy_addons:
    copy_addons()
    __copy_addons = True
