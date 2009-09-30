from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import SuspiciousOperation
from crunchyfrog import media_cache

def media_by_token(request, token, template_name):
    try:
        return HttpResponse(media_cache.get(token, template_name))
    except SuspiciousOperation as so:
        return HttpResponseNotFound(so)
