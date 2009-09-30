import mimetypes

from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import SuspiciousOperation
from crunchyfrog import media_cache

def media_by_token(request, token, template_name):
    try:
        mimetype = mimetypes.guess_type(template_name)[0] or 'application/octet-stream'
        return HttpResponse(media_cache.get(token, template_name), mimetype=mimetype)
    except SuspiciousOperation as so:
        return HttpResponseNotFound(so)
