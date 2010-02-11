import time

from django.conf import settings
from django.template import loader, TemplateDoesNotExist
from django.http import HttpResponse
from django.utils import simplejson

from crunchyfrog import RequestContext
from crunchyfrog.page import PageAssembly
from crunchyfrog.ribt import test_registry, is_instrumented, instrument_site

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
    })

    pa = PageAssembly('ribt/testrunner/display/display.yaml', context)
    return pa.get_http_response()

def interface_shutdown(request):
    """
    Called at the end of the test run, de-instuments the site for testing
    """
    instrument_site(False)

def subject_start(request):
    """
    Is the temporary page we see as the test runner is bootstrapping, it gives
    us some brief information before the test runs start
    """
    context = RequestContext(request)
    pa = PageAssembly('ribt/testrunner/subjectstart/subjectstart.yaml', context)
    return pa.get_http_response()

# Don't test this module
setattr(testrunner, '__test__', False)
