import os
import shutil

from django import http, template
from django.core.cache import cache
from crunchyfrog.conf import settings

__all__ = ['clear_page_assembly_cache', 'HttpResponse', 'RequestContext']

def clear_page_assembly_cache():
    from crunchyfrog.assembly import PAGE_ASSEMBLY_CACHE_KEY
    cache_dict = cache.get(PAGE_ASSEMBLY_CACHE_KEY)
    for key in cache_dict:
        cache.delete(key)
    cache.set(PAGE_ASSEMBLY_CACHE_KEY, [])

def clear_media_cache():
    cachedir = settings.CRUNCHYFROG_CACHE_ROOT
    if os.path.isdir(cachedir):
        shutil.rmtree(cachedir)

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
