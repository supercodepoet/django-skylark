from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.conf import settings
from django.core.urlresolvers import reverse

def urls():
    from django.conf.urls.defaults import patterns, url, include
    return patterns('crunchyfrog.views',
        url(r'^(?P<token>[0-9]+)/(?P<template_name>.*)$',
            'media_by_token',
            name='media-by-token'),
    ), 'crunchyfrog', 'crunchyfrog'

class MediaCache(object):
    def __init__(self):
        if not settings.CACHE_BACKEND:
            raise ImproperlyConfigured('settings.CACHE_BACKEND needs to be \
               specified, use locmem:// if you do not wish to setup memcached \
               or some other alternative')

        self._tokens = cache

        # How long should we keep the cached templates in the cache?
        self.timeout_seconds = 60 * 5

    def _get_token(self, context):
        return str(id(context))

    def add(self, template_name, context, template_rendered):
        token = self._get_token(context)

        rendered_list = self._tokens.get(token) or {}

        rendered_list[template_name] = template_rendered

        self._tokens.set(token, rendered_list, self.timeout_seconds)

        return reverse('crunchyfrog:media-by-token', kwargs={'template_name': template_name, 'token': token})

    def get(self, token, template_name):
        rendered_list = self._tokens.get(str(token))

        if not rendered_list or not template_name in rendered_list:
            raise SuspiciousOperation('The rendered media for token %s and template name %s was not found.' % (token, template_name,))

        return rendered_list[template_name] 

media_cache = MediaCache()
urls = urls()
