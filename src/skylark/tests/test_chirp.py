import sys
import py.test

from nose.tools import with_setup
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from skylark import *
from skylark.assembly import *
from skylark.page import PageAssembly
from skylark.snippet import SnippetAssembly
from django.conf import settings

from skylark.tests import *
from skylark import chirp


def teardown_chirp():
    teardown()
    chirp.instrument_site(False)
    chirp.test_registry.clear()


@with_setup(setup, teardown_chirp)
def test_instrument():
    assert not chirp.is_instrumented()
    chirp.instrument_site(True)
    py.test.raises(chirp.ChirpError, chirp.instrument_site, True)
    assert chirp.is_instrumented()
    chirp.instrument_site(False)
    assert not chirp.is_instrumented()
    settings.SKYLARK_CHIRP_INSTRUMENTED = True
    # This only get's triggered if we render a page, so let's do that
    request = get_request_fixture()
    c = RequestContext(request, {})
    sa = SnippetAssembly('dummyapp/snippet/snippet.yaml', c)
    content = sa.dumps()
    assert chirp.is_instrumented()
    settings.SKYLARK_CHIRP_INSTRUMENTED = False


@with_setup(setup, teardown_chirp)
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
        'out/dynamicapp/media/js/chirploaded.js',
        'out/dynamicapp/media/js/templates/chirploaded.html',
    )

    assert 'This is my snippet test' in content
                              

@with_setup(setup, teardown_chirp)
def test_chirp_renders_in_page():
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/chirp.yaml', c)

    content = pa.dumps()

    exist(
        'addon/dojo/dojo.js',
        'addon/dojox/timing/_base.js',
        'out/dummyapp/page/media/img/notreferenced.png',
        'out/dummyapp/page/media/img/test.png',
        'out/dummyapp/page/media/js/sample.js',
        'out/dummyapp/page/media/js/templates/notreferenced.html',
        'out/dummyapp/page/media/js/templates/sample.js',
        'out/dummyapp/tag/media/css/screen.css',
        'out/dummyapp/tag/media/img/testimage.png',
        'out/dummyapp/tag/media/js/templates/test.html',
        'out/dynamicapp/media/js/chirploaded.js',
        'out/dynamicapp/media/js/templates/chirploaded.html',
    )

    assert "dojo.registerModulePath('DynamicApp.Page'" in content
    assert "dojo.require('DynamicApp.Page.Controller');" in content
    assert "dojo.require('DynamicApp.Page.View');" in content
    assert 'dummyapp/tag/media/css/screen.css' in content
    assert 'dummyapp/page/media/js/sample.js' in content
    assert 'media/cfcache/out/dynamicapp' in content
    assert 'addon/dojo/dojo.js' in content


@with_setup(setup, teardown_chirp)
def test_chirp_dojo_settings():
    settings.SKYLARK_DOJO_VIA_CDN_AOL = True

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/chirp.yaml', c)
    content = pa.dumps()
    assert 'http://o.aolcdn.com/dojo/1.4/dojo/dojo.xd.js' in content

    settings.SKYLARK_DOJO_VIA_CDN_AOL = None

    settings.SKYLARK_DOJO_VIA_URL = 'http://testdojo.com/dojo.js'

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/chirp.yaml', c)
    content = pa.dumps()
    assert 'http://testdojo.com/dojo.js' in content

    settings.SKYLARK_DOJO_VIA_URL = None


@with_setup(setup, teardown_chirp)
def test_chirp_test_registry_add():
    py.test.raises(chirp.ChirpError, chirp.test_registry.add, None)

    chirp.test_registry.add('/someurl', name='Some Test')

    names = [ i.name for i in chirp.test_registry.list() ]
    urls = [ i.url for i in chirp.test_registry.list() ]

    assert '/someurl' in chirp.test_registry
    assert '/nothere' not in chirp.test_registry
    assert '/someurl' in urls
    assert 'Some Test' in names

    chirp.test_registry.add('/another', name='A special test')

    assert len(chirp.test_registry) == 2


@with_setup(setup, teardown_chirp)
def test_chirp_autodiscover():
    chirp.autodiscover()
    assert 'dummyapp.chirp' in chirp._chirp_modules

    chirp.instrument_site(True)
    assert 'dummyapp.chirp' in sys.modules


@with_setup(setup, teardown_chirp)
def test_chirp_testcase_is_included():
    assert not chirp.is_instrumented()
    chirp.instrument_site(True)

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/chirp.yaml', c)
    content = pa.dumps()

    assert 'dojo.require(\'ChirpTools.TestRunner' in content
    assert 'dojo.require(\'ChirpTools.Mvc' in content
    assert 'ChirpTools.TestRunner.TestCaseCollector' in content


@with_setup(setup, teardown_chirp)
def test_chirp_includes_tests():
    assert not chirp.is_instrumented()
    chirp.instrument_site(True)

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/chirp.yaml', c)
    content = pa.dumps()

    assert "dojo.require('DynamicApp.Page.Test')" in content

    chirp.instrument_site(False)

    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/chirp.yaml', c)
    content = pa.dumps()

    assert "dojo.require('DynamicApp.Page.Test')" not in content
