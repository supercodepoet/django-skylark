import sys
import py.test

from nose.tools import with_setup
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from crunchyfrog import *
from crunchyfrog.assembly import *
from crunchyfrog.page import PageAssembly
from crunchyfrog.snippet import SnippetAssembly
from django.conf import settings

from crunchyfrog.tests import *
from crunchyfrog import ribt

@attr('focus')
def test_instrument():
    assert not ribt.is_instrumented()
    ribt.instrument_site(True)
    py.test.raises(ribt.RibtError, ribt.instrument_site, True)
    assert ribt.is_instrumented()
    ribt.instrument_site(False)
    assert not ribt.is_instrumented()
    settings.CRUNCHYFROG_RIBT_INSTRUMENTED = True
    # This only get's triggered if we render a page, so let's do that
    request = get_request_fixture()
    c = RequestContext(request, {})
    sa = SnippetAssembly('dummyapp/snippet/snippet.yaml', c)
    content = sa.dumps()
    assert ribt.is_instrumented()
    settings.CRUNCHYFROG_RIBT_INSTRUMENT = False

@with_setup(setup, teardown)
def test_snippet_render():
    request = get_request_fixture()
    c = RequestContext(request, {})
    sa = SnippetAssembly('dummyapp/snippet/snippet.yaml', c)

    content = sa.dumps()

    assert not '<html' in content
    assert not '<head' in content
    assert not '<body' in content
    assert not '<link' in content

    assert "dojo.registerModulePath('DynamicApp.Snippet'" in content

    exist(
        'se/dynamicapp/media/js/ribtloaded.js',
        'se/dynamicapp/media/js/templates/ribtloaded.html',
    )

    assert 'This is my snippet test' in content
                              
@with_setup(setup, teardown)
def test_ribt_renders_in_page():
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/ribt.yaml', c)

    content = pa.dumps()

    exist(
        'addon/dojo/dojo.js',
        'addon/dojo/dojox_for_ribt.js',
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/sample.js',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
        'se/dummyapp/tag/media/css/screen.css',
        'se/dummyapp/tag/media/img/testimage.png',
        'se/dummyapp/tag/media/js/templates/test.html',
        'se/dynamicapp/media/js/ribtloaded.js',
        'se/dynamicapp/media/js/templates/ribtloaded.html',
    )

    assert "dojo.registerModulePath('DynamicApp.Page'" in content
    assert "dojo.require('DynamicApp.Page.Controller');" in content
    assert "dojo.require('DynamicApp.Page.View');" in content
    assert 'dummyapp/tag/media/css/screen.css' in content
    assert 'dummyapp/page/media/js/sample.js' in content
    assert 'media/cfcache/se/dynamicapp' in content
    assert 'addon/dojo/dojo.js' in content
    assert 'addon/dojo/dojox_for_ribt.js' in content

@with_setup(setup, teardown)
def test_ribt_dojo_settings():
    settings.CRUNCHYFROG_DOJO_VIA_CDN_AOL = True

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/ribt.yaml', c)
    content = pa.dumps()
    assert 'http://o.aolcdn.com/dojo/1.4/dojo/dojo.xd.js' in content

    settings.CRUNCHYFROG_DOJO_VIA_CDN_AOL = None

    settings.CRUNCHYFROG_DOJO_VIA_URL = 'http://testdojo.com/dojo.js'

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/ribt.yaml', c)
    content = pa.dumps()
    assert 'http://testdojo.com/dojo.js' in content

    settings.CRUNCHYFROG_DOJO_VIA_URL = None

    settings.CRUNCHYFROG_DOJO_VIA_PATH = '/media/somedojohere/dojo.js'

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/ribt.yaml', c)
    content = pa.dumps()
    assert '/media/somedojohere/dojo.js' in content

    settings.CRUNCHYFROG_DOJO_VIA_PATH = None

def test_ribt_test_registry_add():
    py.test.raises(ribt.RibtError, ribt.test_registry.add, None)

    ribt.test_registry.add('/someurl', name='Some Test')

    assert '/someurl' in ribt.test_registry
    assert '/nothere' not in ribt.test_registry
    assert '/someurl' == ribt.test_registry.list()[0].url
    assert 'Some Test' == ribt.test_registry.list()[0].name

    ribt.test_registry.add('/another', name='A special test')

    assert len(ribt.test_registry) == 2

def test_ribt_autodiscover():
    ribt.autodiscover()
    assert 'dummyapp.ribt' in ribt._ribt_modules

    ribt.instrument_site(True)
    assert 'dummyapp.ribt' in sys.modules

    ribt.instrument_site(False)

@with_setup(setup, teardown)
def test_ribt_testcase_is_included():
    assert not ribt.is_instrumented()
    ribt.instrument_site(True)

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/ribt.yaml', c)
    content = pa.dumps()

    assert 'ribt/testrunner/media/js/testcase.js' in content

    ribt.instrument_site(False)

@with_setup(setup, teardown)
def test_ribt_includes_tests():
    assert not ribt.is_instrumented()
    ribt.instrument_site(True)

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/ribt.yaml', c)
    content = pa.dumps()

    assert "dojo.require('DynamicApp.Page.Test')" in content

    ribt.instrument_site(False)

    content = pa.dumps()

    assert "dojo.require('DynamicApp.Page.Test')" not in content
