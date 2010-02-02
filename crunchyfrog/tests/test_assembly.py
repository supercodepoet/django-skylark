import py.test
import re

from os.path import isdir, isfile, join
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
def test_creates_files_in_cache():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/sample.yaml', c)

    pa.dumps()

    exist(
        'se/dummyapp/page/media/css/sample.css',
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/notreferenced.js',
        'se/dummyapp/page/media/js/sample.js',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
    )

    from crunchyfrog import clear_media_cache
    clear_media_cache()
    assert not isdir(cachedir)

@with_setup(setup, teardown)
def test_can_render_an_asset():
    request = get_request_fixture()
    c = RequestContext(request, { 'color': 'gray' })
    pa = PageAssembly('dummyapp/page/renderasset.yaml', c)

    content = pa.dumps()

    exist(
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
    )

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

    media = (cachedir, 'se', 'dummyapp', 'page', 'media')
    css = get_contents(join(*media + ('css', 'clevercss.css')))
    assert css == 'body {\n  background-color: gray;\n}'

    exist(
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
    )

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

    exist(
        'se/dummyapp/page/media/css/sample.css',
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/notreferenced.js',
        'se/dummyapp/page/media/js/sample.js',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
    )

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

    content = pa.dumps()

    exist(
        'se/dummyapp/page/media/css/sample.css',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/js/templates/sample.js',
        'se/dummyapp/page/media/js/notreferenced.js',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
    )

    assert content.find('notreferenced') == -1, 'Found a reference to a file that has been set include: false in the yaml file.  It should not show up in the rendered output'

@with_setup(setup, teardown)
def test_references_other_yaml_files():
    request = get_request_fixture()
    c = RequestContext(request, { 'background_color': 'red' })
    pa = PageAssembly('dummyapp/page/uses.yaml', c)

    content = pa.dumps()

    exist(
        'se/dummyapp/page/media/css/sample.css',
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/notreferenced.js',
        'se/dummyapp/page/media/js/sample.js',
        'se/dummyapp/page/media/js/sampleafter.js',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
    )

    assert len(re.findall('.*\.css', content)) == 2, 'There should be 2 css files from the sample.yaml in here'
    assert content.find('sample.js') < content.find('sampleafter.js'), 'The sample.js should come before the sampleafter.js'
    assert "body {" in content
    assert "background-color: red" in content

@with_setup(setup, teardown)
@attr('focus')
def test_renders_meta_section():
    request = get_request_fixture()
    c = RequestContext(request, { 'foo': 'bar' })
    pa = PageAssembly('dummyapp/page/meta.yaml', c)

    content = pa.dumps()

    exist(
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
    )

    assert '<meta http-equiv="test" content="test-content">' in content
    assert '<meta name="test-meta" content="foo">' in content

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
    assert len(pa.dumps().split("\n")) == 40 

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

    exist(
        'se/dummyapp/page/media/css/sample.css',
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/notreferenced.js',
        'se/dummyapp/page/media/js/sample.js',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
    )

@with_setup(setup, teardown)
def test_add_yaml_decorator():
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/tag.yaml', c)

    content = pa.dumps()

    exist(
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
        'se/dummyapp/tag/media/css/screen.css',
        'se/dummyapp/tag/media/img/testimage.png',
        'se/dummyapp/tag/media/js/templates/test.html',
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

    exist(
        'se/dynamicapp/media/js/dojoloaded.js',
        'se/dynamicapp/media/js/templates/dojoloaded.html',
    )

    assert 'This is my snippet test' in content

@with_setup(setup, teardown)
def test_dojo_renders_in_page():
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/dojo.yaml', c)

    content = pa.dumps()

    exist(
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/sample.js',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
        'se/dummyapp/tag/media/css/screen.css',
        'se/dummyapp/tag/media/img/testimage.png',
        'se/dummyapp/tag/media/js/templates/test.html',
        'se/dynamicapp/media/js/dojoloaded.js',
        'se/dynamicapp/media/js/templates/dojoloaded.html',
    )

    assert "dojo.registerModulePath('DynamicApp.Page'" in content
    assert "dojo.require('DynamicApp.Page.Controller');" in content
    assert "dojo.require('DynamicApp.Page.View');" in content
    assert 'dummyapp/tag/media/css/screen.css' in content
    assert 'dummyapp/page/media/js/sample.js' in content
    assert 'media/cfcache/se/dynamicapp' in content


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

    settings.CRUNCHYFROG_PLANS = 'mediadeploy_reusable'

    e = py.test.raises(CssFormatError, pa.dumps)

    assert 'CSSStyleRule' in str(e.value)

    settings.CRUNCHYFROG_RAISE_CSS_ERRORS = False

    assert pa.dumps()

@with_setup(setup, teardown)
def test_cache_in_debug_mode():
    request = get_request_fixture()
    c = RequestContext(request, {})
    pa = PageAssembly('dummyapp/page/sample.yaml', c)

    sample_path = str(template.loader.find_template_source(
        'dummyapp/page/media/js/sample.js'
    )[1])
    temp_path = '%s_temp' % sample_path

    pa.dumps()

    exist(
        'se/dummyapp/page/media/css/sample.css',
        'se/dummyapp/page/media/img/notreferenced.png',
        'se/dummyapp/page/media/img/test.png',
        'se/dummyapp/page/media/js/notreferenced.js',
        'se/dummyapp/page/media/js/sample.js',
        'se/dummyapp/page/media/js/templates/notreferenced.html',
        'se/dummyapp/page/media/js/templates/sample.js',
    )

    content_before = get_contents(join(
        cachedir, 'se', 'dummyapp', 'page', 'media', 'js', 'sample.js')
    )

    # Copy to a temp file and alter the original
    shutil.copyfile(sample_path, temp_path)
    sample_fh = open(sample_path, 'a')
    sample_fh.write('var changed = true;')
    sample_fh.close()

    pa.dumps()
    content_after = get_contents(join(
        cachedir, 'se', 'dummyapp', 'page', 'media', 'js', 'sample.js')
    )

    # Restore the file
    shutil.copyfile(temp_path, sample_path)
    os.remove(temp_path)

    assert content_before != content_after
