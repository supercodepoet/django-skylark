import py.test
import re

from os.path import join
from nose.tools import with_setup
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from crunchyfrog import *
from crunchyfrog.assembly import *
from crunchyfrog.page import PageAssembly
from crunchyfrog.snippet import SnippetAssembly

from crunchyfrog.tests import *

@with_setup(setup, teardown)
def test_issue_07():
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
    sa = SnippetAssembly('dummyapp/issue07/issue07.yaml', c)

    content = sa.dumps()

    exist(
        'se/dummyapp/issue07/media/js/Class.js',
        'se/dummyapp/issue07/media/js/templates/file.html',
    )

@with_setup(setup, teardown)
def test_issue_19():
    """
    Issue #19

    If DEBUG=False, a cached directory may not contain all needed files

    With DEBUG=False, an existing directory will be ignored when creating the
    files within the cfcache.  The reason that this creates a problem, is that
    the directory may be created by another directive like js: -file:
    app/page/media/js/file.js and then another directive may add content to
    that same directory ribt: -location: app/page/media/js. The first js
    will create the directory and the ribt section will then be skipped.
    """
    settings.DEBUG = False
    settings.CRUNCHYFROG_PLANS = 'mediadeploy'
    settings.CRUNCHYFROG_PLANS_DEFAULT = 'rf'

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/issue19/issue19.yaml', c)

    content = pa.dumps()

    exist(
        'rf/dummyapp/issue19/media/js/static.js',
        'rf/dummyapp/issue19/media/js/Class.js',
        'rf/dummyapp/issue19/media/js/templates/file.html',
    )

@with_setup(setup, teardown)
def test_issue_23():
    """
    Issue #23

    If you are rendering a page with a PageAssembly and that page contains a
    template tag that renders using SnippetAssembly, the underlying
    context['page_instructions'] object will be changed causing dependencies to
    be missed
    """
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/issue23/issue23.yaml', c)

    assert 'dummyapp/issue23/media/js/tt_after_sa.js' in pa.dumps()

@with_setup(setup, teardown)
def test_issue_25():
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
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_reusable'

    hash_js = '2a89c79723ce8d1d558232e113afcae8'

    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/issue25/issue25.yaml', c)

    content = pa.dumps()

    assert content

    jsfile = get_contents(
        os.path.join(cachedir, 'rf', '%s.js' % hash_js)
    )

    assert "dojo.registerModulePath('RibtTools'" in jsfile
    assert "dojo.provide('RibtTools.Error')" in jsfile
    assert 'dojo.provide("dojox.timing._base")' in jsfile
    assert 'dojo.provide("dojox.timing")' in jsfile
    assert "dojo.provide('RibtTools.SyncTimer.Timer')" in jsfile
    assert 'dojo.provide("dojo.back")' in jsfile
    assert 'dojo.provide("dojo.NodeList-traverse")' in jsfile
    assert "dojo.registerModulePath('DummyApp.Issue25'" in jsfile
    assert "dojo.provide('DummyApp.Issue25.TestFile')" in jsfile
