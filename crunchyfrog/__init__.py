import os
import shutil

from django import http, template
from django.core.cache import cache
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

class RequestContext(template.RequestContext):
    """
    Adds the raw request to the object, we need this to perform some caching work
    later on
    """
    def __init__(self, request, dict=None, processors=None):
        super(RequestContext, self).__init__(request, dict, processors)
        self.request = request

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

