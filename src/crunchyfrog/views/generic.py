from functools import partial
from django import http
from django.conf import settings
from django.template import loader, TemplateDoesNotExist
from crunchyfrog import RequestContext
from crunchyfrog.page import PageAssembly

def direct_to_yaml(yaml_file, **kwargs):
    if settings.DEBUG:
        # Let's make sure we can grab this
        loader.find_template_source(yaml_file)

    def render(request, **kwargs):
        response = kwargs.get('response_object')
        yaml_file = kwargs.get('yaml_file')
        context = RequestContext(request)
        pa = PageAssembly(yaml_file, context)
        return response(pa.dumps())

    response_object = kwargs.get('response_object',
        http.HttpResponse)
    func = partial(render, yaml_file=yaml_file,
        response_object=response_object)
    funcname = 'direct_to_yaml%s' % id(func)
    globals()[funcname] = func

    return 'crunchyfrog.views.generic.%s' % funcname

def render_404_from_yaml(yaml_file):
    return direct_to_yaml(yaml_file,
        response_object=http.HttpResponseNotFound)

def render_500_from_yaml(yaml_file):
    return direct_to_yaml(yaml_file,
        response_object=http.HttpResponseServerError)
