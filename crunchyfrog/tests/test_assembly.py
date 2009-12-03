import py.test
import os
import re

from nose.tools import with_setup
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from crunchyfrog import *
from crunchyfrog.assembly import *
from crunchyfrog.page import PageAssembly
from crunchyfrog.plans.base import CssFormatError
from crunchyfrog.snippet import SnippetAssembly
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.core.cache import cache
from yaml.parser import ParserError

from crunchyfrog.tests import *

def test_can_not_create_page_assembly():
    py.test.raises(TypeError, "pa = PageAssembly()")
    py.test.raises(TypeError, 'pa = PageAssembly("somefile/test.yaml")')

    """ Make sure that the context is correct """
    c = []
    py.test.raises(ValueError, 'pa = PageAssembly("somefile/test.yaml", c)')

    """ Make sure that you can't send it an empty yaml file """
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    py.test.raises(ValueError, 'pa = PageAssembly((), c)')

def test_can_create_page_assembly():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('somefile/that/doesnt/exist.yaml', c)

    assert isinstance(pa, PageAssembly)

    """ We should be able to pass it a tuple with more than one file in it """
    pa = PageAssembly(('somefile/that/doesnt/exist.yaml', 'someother/file.yaml'), c)

def test_missing_template():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('somefile/that/doesnt/exist.yaml', c)

    py.test.raises(TemplateDoesNotExist, "pa.get_http_response()")

def test_provides_page_instructions():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/invalid.yaml', c)

    py.test.raises(ParserError, pa.get_http_response)

def test_missing_crunchyfrog_settings():
    from crunchyfrog.conf import settings

    assert settings.MEDIA_URL
    assert settings.MEDIA_ROOT
    assert settings.CRUNCHYFROG_CACHE_ROOT
    assert settings.CRUNCHYFROG_CACHE_URL

@with_setup(setup, teardown)
def test_returns_http_response():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/sample.yaml', c)

    assert isinstance(pa.get_http_response(), HttpResponse)

@with_setup(setup, teardown)
def test_include_with_inline():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/includeinline.yaml', c)

    py.test.raises(AttributeError, pa.get_http_response)

@with_setup(setup, teardown)
def test_creates_a_file_in_cache():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/sample.yaml', c)

    assert not os.path.isdir(cachedir)

    pa.dumps()

    assert get_one_file_in(cachedir)

    from crunchyfrog import clear_media_cache
    clear_media_cache()
    assert not os.path.isdir(cachedir)

@with_setup(setup, teardown)
def test_creates_a_file_in_cache_with_key():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/sample.yaml', c, 'fileincachewithkey')

    assert not os.path.isdir(cachedir)

    pa.dumps()

    assert get_one_file_in(cachedir)

@with_setup(setup, teardown)
def test_can_render_an_asset():
    request = get_request_fixture()
    c = RequestContext(request, { 'color': 'gray' })
    pa = PageAssembly('dummyapp/page/renderasset.yaml', c)

    content = pa.dumps()

    assert 'my_favorite_color = "gray"' in content
    assert 'background-color: gray' in content

@with_setup(setup, teardown)
def test_can_detect_bad_processor():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/badprocessor.yaml', c)

    py.test.raises(AttributeError, pa.get_http_response)

@with_setup(setup, teardown)
def test_can_render_clevercss():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/clevercss.yaml', c)

    pa.dumps()

    css = get_contents(get_one_file_in(cachedir))

    assert css == 'body {\n    background-color: gray\n    }'

@with_setup(setup, teardown)
def test_missing_yaml_attributes():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/missingbody.yaml', c)

    py.test.raises(AssertionError, pa.get_http_response)

    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/missingtitle.yaml', c)

    py.test.raises(AssertionError, pa.get_http_response)

    # Combining them should fix our issue
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly(('dummyapp/page/missingbody.yaml', 'dummyapp/page/missingtitle.yaml'), c)

    content = pa.dumps()

    assert isinstance(content, unicode), 'The returned value from dumps() did not return a unicode instance, instead the value was %r' % content 

@with_setup(setup, teardown)
def test_will_not_duplicate_assets():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/duplicateassets.yaml', c)

    content = pa.dumps()

    assert len(re.findall('sample.js', content)) == 1
    assert len(re.findall('files.js', content)) == 1

@with_setup(setup, teardown)
def test_title_tag_is_escaped():
    request = get_request_fixture()
    c = RequestContext(request, { 'title': unicode('Title < > \' "') })
    pa = PageAssembly('dummyapp/page/escapetitle.yaml', c)

    content = pa.dumps()

    assert content.index('Title &lt; &gt; &#39; &quot;')

@with_setup(setup, teardown)
def test_will_copy_assets():
    request = get_request_fixture()
    c = RequestContext(request, { 'title': unicode('Title < > \' "') })
    pa = PageAssembly('dummyapp/page/sample.yaml', c)

    filenames = ('dummyapp/page/media/img/test.png',
                 'dummyapp/page/media/img/notreferenced.png',
                 'dummyapp/page/media/js/templates/sample.js',
                 'dummyapp/page/media/js/notreferenced.js',
                 'dummyapp/page/media/js/templates/notreferenced.html',
                )

    content = pa.dumps()

    assert content.find('notreferenced') == -1, 'Found a reference to a file that has been set include: false in the yaml file.  It should not show up in the rendered output'

    for template_name in filenames:
        assert os.path.isfile(os.path.join(cachedir, 'se', template_name))

@with_setup(setup, teardown)
def test_uses_the_page_instructions_cache_if_enabled():
    settings.CACHE_BACKEND = 'locmem://'
    orig_debug = settings.DEBUG
    settings.DEBUG = False

    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/sample.yaml', c, 'samecachekey')
    first_content = pa.dumps()

    page_assembly_cache = cache.get(PAGE_ASSEMBLY_CACHE_KEY)
    assert len(page_assembly_cache) == 1

    pa = PageAssembly('dummyapp/page/invalid.yaml', c, 'samecachekey')
    second_content = pa.dumps()

    page_assembly_cache = cache.get(PAGE_ASSEMBLY_CACHE_KEY)
    assert len(page_assembly_cache) == 1

    assert first_content == second_content

    # Restore the debug setting
    settings.DEBUG = orig_debug

@with_setup(setup, teardown)
def test_can_clear_page_assembly_cache():
    settings.CACHE_BACKEND = 'locmem://'
    orig_debug = settings.DEBUG
    settings.DEBUG = False

    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/sample.yaml', c, 'samecachekey')
    content = pa.dumps()

    # Restore the debug setting
    settings.DEBUG = orig_debug

    page_assembly_cache = cache.get(PAGE_ASSEMBLY_CACHE_KEY)
    a_pa_key = page_assembly_cache[0]
    assert len(page_assembly_cache) == 1
    assert cache.get(a_pa_key)

    clear_page_assembly_cache()

    assert not cache.get(PAGE_ASSEMBLY_CACHE_KEY)
    assert not cache.get(a_pa_key)

@with_setup(setup, teardown)
def test_references_other_yaml_files():
    request = get_request_fixture()
    c = RequestContext(request, { 'background_color': 'red' })
    pa = PageAssembly('dummyapp/page/uses.yaml', c)

    content = pa.dumps()

    assert len(re.findall('.*\.css', content)) == 2, 'There should be 2 css files from the sample.yaml in here'
    assert content.find('sample.js') < content.find('sampleafter.js'), 'The sample.js should come before the sampleafter.js'
    assert "body {" in content
    assert "background-color: red" in content

@with_setup(setup, teardown)
def test_renders_meta_section():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/meta.yaml', c)

    content = pa.dumps()

    assert content.find('<meta http-equiv="test" content="test-content">') >= 0, 'Could not locate the meta information expected'

@with_setup(setup, teardown)
def test_will_do_conditional_comments():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/ieversion.yaml', c)

    content = pa.dumps()

    # For the CSS
    assert '<!--[if gte IE 6]>' in content
    # This is for the JS, which we also support
    assert '<!--[if gte IE 7]>' in content

@with_setup(setup, teardown)
def test_will_tidy_output():
    assert settings.DEBUG
    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('dummyapp/page/sample.yaml', c)
    assert len(pa.dumps().split("\n")) == 38 

@with_setup(setup, teardown)
def test_will_use_correct_doctype():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/sample.yaml', c)

    content = pa.dumps()

    assert '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN' in content
    assert 'html4/loose.dtd' in content

    pa = PageAssembly('dummyapp/page/xhtmlstrict.yaml', c)

    content = pa.dumps()

    assert '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"' in content
    assert 'xhtml1-strict.dtd' in content

@with_setup(setup, teardown)
def test_add_yaml_decorator():
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/tag.yaml', c)

    content = pa.dumps()

    assert get_one_file_in(os.path.join(
        cachedir, 'se', 'dummyapp', 'tag', 'media', 'css')
    )

    assert 'This is my tag test' in content
    assert '/media/cfcache/se/dummyapp/tag/media/css/screen.css" media="screen"' in content
                              
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

    assert get_one_file_in(os.path.join(
        cachedir, 'se', 'dynamicapp', 'media', 'js')
    )

    assert 'This is my snippet test' in content

@with_setup(setup, teardown)
def test_dojo_renders_in_page():
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/dojo.yaml', c)

    content = pa.dumps()

    assert "dojo.registerModulePath('DynamicApp.Page'" in content
    assert "dojo.require('DynamicApp.Page.Controller');" in content
    assert "dojo.require('DynamicApp.Page.View');" in content
    assert 'dummyapp/tag/media/css/screen.css' in content
    assert 'dummyapp/page/media/js/sample.js' in content
    assert 'media/cfcache/se/dynamicapp' in content

@with_setup(setup, teardown)
def test_stale_assets_regarding_dojo():
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
    sa = SnippetAssembly('dummyapp/staleassets/staleassets.yaml', c)

    content = sa.dumps()
    file = get_one_file_in(os.path.join(
        cachedir, 'se', 'dummyapp', 'staleassets', 'media', 'js')
    )

    assert 'Class.js' in file

@with_setup(setup, teardown)
def test_bad_html():
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/badhtml.yaml', c)

    e = py.test.raises(HtmlTidyErrors, pa.dumps)

    assert 'line 22' in str(e.value)
    assert "Warning: <tag> missing '>'" in str(e.value)

    settings.CRUNCHYFROG_RAISE_HTML_ERRORS = False

    assert pa.dumps()

@with_setup(setup, teardown)
def test_bad_css():
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/badcss.yaml', c)

    e = py.test.raises(CssFormatError, pa.dumps)

    assert 'CSSStyleRule' in str(e.value)

    settings.CRUNCHYFROG_RAISE_CSS_ERRORS = False

    assert pa.dumps()

