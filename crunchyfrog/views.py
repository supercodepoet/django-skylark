import mimetypes

from urlparse import urljoin
from django.http import HttpResponse, HttpResponseNotFound, HttpResponsePermanentRedirect
from django.core.exceptions import SuspiciousOperation
from crunchyfrog import media_cache
from crunchyfrog.conf.default import *

def media_by_token(request, token, template_name):
    try:
        mimetype = mimetypes.guess_type(template_name)[0] or 'application/octet-stream'

        if mimetype.find('image') > -1:
            """
            ============
            Hack warning
            ============
            This is horrible.  This is a huge hack and needs to be fixed soon
            
            What's going on here is that sometimes we render CSS files and the
            serving of those files ends up coming from this view.

            Inside the CSS file you see this a log img(../img/something.gif).
            This is a great feature of CSS because the browser works out the path
            of the image relative to the CSS file.

            This doesn't work well for us though.  Because we are dynamically
            serving the CSS.  So the browser works out a path that comes from
            /cfmedia/TOKEN/TEMPLATE_NAME.  It simply isn't there.

            A couple of ways to solve this:
            -------------------------------
                * Create a template variable {{ MEDIA_PATH }} so that CSS
                  authors can say img({{ MEDIA_PATH}}/img/something.gif)
                * Rewrite the CSS on the fly as we render, replacing
                  img(../img/something.gif) with 
                  img(/media/cfcache/app/page/media/img/something.gif)
            """
            url = urljoin(CRUNCHYFROG_CACHE_URL, template_name)
            return HttpResponsePermanentRedirect(url)

        return HttpResponse(media_cache.get(token, template_name), mimetype=mimetype)
    except SuspiciousOperation, so:
        return HttpResponseNotFound(so)
