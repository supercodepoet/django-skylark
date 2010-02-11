from django.http import HttpResponse
from crunchyfrog.page import PageAssembly, RequestContext

def list(request):
    c = RequestContext(request, {
        'confection': "Ram's bladder cup"
    })

    pa = PageAssembly('goodies/list/list.yaml', c)

    return pa.get_http_response()
