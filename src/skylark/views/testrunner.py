import time

from django.conf import settings
from django.template import loader, TemplateDoesNotExist
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils import simplejson 

from skylark import RequestContext
from skylark.page import PageAssembly
from skylark.chirp import test_registry, is_instrumented, instrument_site


def testrunner(request):
    """
    Main view to load the interface and start running the tests
    """
    return interface_start(request)


def interface_start(request):
    """
    Provides the main HTML for the test runner
    """
    if not is_instrumented():
        instrument_site(True)
    teps = [ i.__dict__ for i in test_registry.list() ]
    context = RequestContext(request, {
        'test_count': len(test_registry),
        'test_entry_points_json': simplejson.dumps(teps),
        'url_deinstrument': reverse(deinstrument),
    })

    pa = PageAssembly('chirp/testrunner/display/display.yaml', context)
    return pa.get_http_response()


def deinstrument(request):
    """
    Called at the end of the test run, de-instuments the site for testing
    """
    instrument_site(False)
    return HttpResponse()


def subject_start(request):
    """
    Is the temporary page we see as the test runner is bootstrapping, it gives
    us some brief information before the test runs start
    """
    context = RequestContext(request)
    pa = PageAssembly('chirp/testrunner/subjectstart/subjectstart.yaml', context)
    return pa.get_http_response()

# Don't test this module
setattr(testrunner, '__test__', False)
