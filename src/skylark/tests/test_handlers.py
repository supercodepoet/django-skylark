import py.test

from os.path import join
from nose.tools import with_setup
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from django.test.client import Client
from django.core.urlresolvers import get_mod_func
from django.utils.importlib import import_module
from django.http import HttpResponseNotFound, HttpResponseServerError

from skylark.tests.urls import handler404, handler500
from skylark.tests import *

@with_setup(setup, teardown)
def test_handler_404():
    settings.DEBUG = False

    client = Client()
    response = client.get('/something/we/know/is/not/there')
    content = response.content

    assert isinstance(response, HttpResponseNotFound)
    assert '<h1>404</h1>' in content

@with_setup(setup, teardown)
def test_handler_500():
    settings.DEBUG = False
    mod_name, func_name = get_mod_func(handler500)
    callback = getattr(import_module(mod_name), func_name), {}
    response = callback[0](get_request_fixture())

    content = response.content

    assert isinstance(response, HttpResponseServerError)
    assert '<h1>500</h1>' in content
