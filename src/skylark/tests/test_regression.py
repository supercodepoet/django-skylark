import py.test
import re

from os.path import join
from nose.tools import with_setup
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from django.template import TemplateSyntaxError
from skylark import *
from skylark.assembly import *
from skylark.page import PageAssembly
from skylark.snippet import SnippetAssembly

from skylark.tests import *


@with_setup(setup, teardown)
def test_bb_issue_07():
    """
    Issue #7

    The problem that this test is verifying is related to the media/js/templates
    directory being copied before other files in the directory.  Our method that
    checks to see if that directory is stale (needs to be updated) was
    malfunctioning.  It compared the dates on the source and cache directory,
    since they were the same (because we just copied the templates directory) it
    was not allowing the rest of the files to be copied.
    """
    request = get_request_fixture()
    c = RequestContext(request, {})
    sa = SnippetAssembly('dummyapp/issue_bb_07/issue_bb_07.yaml', c)

    content = sa.dumps()

    exist(
        'out/dummyapp/issue_bb_07/media/js/Class.js',
        'out/dummyapp/issue_bb_07/media/js/templates/file.html',
    )


@with_setup(setup, teardown)
def test_bb_issue_19():
    """
    Issue #19

    If DEBUG=False, a cached directory may not contain all needed files

    With DEBUG=False, an existing directory will be ignored when creating the
    files within the cfcache.  The reason that this creates a problem, is that
    the directory may be created by another directive like js: -file:
    app/page/media/js/file.js and then another directive may add content to
    that same directory chirp: -location: app/page/media/js. The first js
    will create the directory and the chirp section will then be skipped.
    """
    settings.DEBUG = False
    settings.SKYLARK_PLANS = 'mediadeploy'
    settings.SKYLARK_PLANS_DEFAULT = 'rf'

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/issue_bb_19/issue_bb_19.yaml', c)

    content = pa.dumps()

    exist(
        'out/dummyapp/issue_bb_19/media/js/static.js',
        'out/dummyapp/issue_bb_19/media/js/Class.js',
        'out/dummyapp/issue_bb_19/media/js/templates/file.html',
    )


@with_setup(setup, teardown)
def test_bb_issue_23():
    """
    Issue #23

    If you are rendering a page with a PageAssembly and that page contains a
    template tag that renders using SnippetAssembly, the underlying
    context['page_instructions'] object will be changed causing dependencies to
    be missed
    """
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/issue_bb_23/issue_bb_23.yaml', c)

    content = pa.dumps()
    stuff = (
        'dummyapp/issue_bb_23/media/js/tt_after_sa.js',
        "dojo.registerModulePath('DummyApp.BB.Issue23.TTSa'",
        "dojo.require('DummyApp.BB.Issue23.TTSa.Controller');",
        "dojo.require('DummyApp.BB.Issue23.TTSa.View');",
        "dojo.registerModulePath('DummyApp.BB.Issue23.TTAfterSa'",
        "dojo.require('DummyApp.BB.Issue23.TTAfterSa.Controller');",
        "dojo.require('DummyApp.BB.Issue23.TTAfterSa.View');",
    )
    for item in stuff:
        assert item in stuff
        assert content.find(item) < content.find("<body>")
        assert content.count(item) == 1


@with_setup(setup, teardown)
def test_bb_issue_24():
    """
    Issue #24

    If the YAML file the SnippetAssembly is rendering does not contain a body, it
    will inherit from the PageAssembly.

    This can cause an infinite loop if there is a templatetag inside the main
    page that is causing the SnippetAssembly to be rendered in the first place.
    """
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/issue_bb_24/issue_bb_24.yaml', c)

    py.test.raises(TemplateSyntaxError, pa.dumps)


@with_setup(setup, teardown)
def test_bb_issue_25():
    """
    Issue #25

    Joe, while debugging a dojo.require problem commented out the line but the
    regular expression does not respect commented sections.
    This test needs to include both commenting styles:

    /**
    dojo.require('something')
    */

    // dojo.require('something')
    """
    # TODO Need to still write a test for block comments
    settings.SKYLARK_PLANS = 'mediadeploy_reusable'

    hash_js = 'bbc01a8493372bb2e9127837ed42dfab'

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/issue_bb_25/issue_bb_25.yaml', c)

    content = pa.dumps()

    assert content

    jsfile = get_contents(
        os.path.join(cachedir, 'out', '%s.js' % hash_js)
    )

    assert "dojo.registerModulePath('ChirpTools'" in jsfile
    assert "dojo.provide('ChirpTools.Error')" in jsfile
    assert 'dojo.provide("dojox.timing._base")' in jsfile
    assert 'dojo.provide("dojox.timing")' in jsfile
    assert "dojo.provide('ChirpTools.SyncTimer.Timer')" in jsfile
    assert 'dojo.provide("dojo.back")' in jsfile
    assert 'dojo.provide("dojo.NodeList-traverse")' in jsfile
    assert "dojo.registerModulePath('DummyApp.BB.Issue25'" in jsfile
    assert "dojo.provide('DummyApp.BB.Issue25.TestFile')" in jsfile


@with_setup(setup, teardown)
def test_bb_issue_27():
    """
    Issue #27

    Because we tack extra information on a context object (namely the page
    instructions and page assemblies that are involving that context) we are
    forced to use the context that is passed into a render method in a template
    tag.

    This is not ideal, because we may overwrite or clog the context with
    variables that don't belong there.

    The template tag needs to be able to create a new RequestContext based on
    the request and have things work out correctly.

    Behind the scenes, CF needs to do whatever is necessary to keep the page
    instructions and page assemblies hooked to the context. This can be done by
    placing a hook on the request itself.
    """
    request = get_request_fixture()

    assert not hasattr(request, 'skylark_internals')

    from django.core import context_processors
    # Add the request object to our contexts
    processors = (
        context_processors.request,
    )

    context = RequestContext(request,
        { 'foo': 'bar' },
        processors)

    assert context.has_key('skylark_internals')
    assert hasattr(request, 'skylark_internals')

    sa_context = RequestContext(context['request'],
        { 'bob': 'slob' },
        processors)

    assert sa_context['skylark_internals'] is request.skylark_internals
    assert sa_context.has_key('bob')
    # Make sure that we aren't inheriting variables
    assert not sa_context.has_key('foo')

    not_hooked_request = get_request_fixture()
    not_hooked_context = RequestContext(not_hooked_request,
        { 'ted': 'sled' },
        processors)

    # Make sure that we aren't reusing request's skylark internals
    assert not_hooked_context['skylark_internals'] is not \
        request.skylark_internals


@with_setup(setup, teardown)
def test_gh_issue_01():
    settings.SKYLARK_PLANS = 'mediadeploy_reusable'

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/issue_gh_01/issue_gh_01.yaml', c)

    content = pa.dumps()
    assert content
