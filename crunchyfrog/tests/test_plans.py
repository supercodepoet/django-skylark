import py.test
import os
from time import sleep

from nose.tools import with_setup
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from django.template import TemplateDoesNotExist

from crunchyfrog import *
from crunchyfrog import ribt
from crunchyfrog import loader
from crunchyfrog.page import PageAssembly
from crunchyfrog.plans import *
from crunchyfrog.plans.base import BadOption
from crunchyfrog.plans.separate import SeparateEverything
from crunchyfrog.plans.fewest import FewestFiles

from crunchyfrog.tests import *

def test_plan_options_invalid():
    py.test.raises(BadOption, plan_options, not_a_valid_option=True)

@with_setup(setup, teardown)
def test_can_change_deploy_plan_name():
    context = {}
    render_full_page = False

    plan = get_for_context(context, render_full_page)
    assert isinstance(plan, SeparateEverything)

    # Make sure that if there is no deploy plan (file missing) that it comes
    # back with SeparateEverything
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_notthere'
    plan = get_for_context(context, render_full_page)
    assert isinstance(plan, SeparateEverything)

    # Change it to something valid that is not the default
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_alt'
    settings.CRUNCHYFROG_PLANS_DEFAULT = 'alternative'
    plan = get_for_context(context, render_full_page)
    assert isinstance(plan, FewestFiles)

    settings.CRUNCHYFROG_PLANS = 'mediadeploy_bad'
    settings.CRUNCHYFROG_PLANS_DEFAULT = 'default'
    py.test.raises(ValueError, get_for_context, context, render_full_page)

    settings.DEBUG = False
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_notthere'
    py.test.raises(MissingMediaPlan, get_for_context, context, render_full_page)

@with_setup(setup, teardown)
def test_deploy_reusable():
    hash_js1 = '93be07cfe9c81198bb4c549c868ff731'
    hash_js2 = '17212bc913552069c1aaec0cb91b3869'
    hash_css = 'ee184e5fad8366ee655a090043693c30'

    settings.DEBUG = False
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_reusable'

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    jsfile = get_contents(
        os.path.join(cachedir, 'rf', '%s.js' % hash_js1)
    )
    assert 'var static_uses2=null;var static_uses1=null;' in jsfile

    jsfile = get_contents(
        os.path.join(cachedir, 'rf', '%s.js' % hash_js2)
    )
    assert jsfile.find('dojo.provide("dojox.timing._base")') < \
        jsfile.find('dojo.provide("dojox.timing")')
    assert jsfile.find("dojo.provide('PlanApp.Page.View')") < \
        jsfile.find("dojo.provide('PlanApp.Page.Controller')")

    cssfile = get_contents(
        os.path.join(cachedir, 'rf', '%s.css' % hash_css)
    )
    assert '.static_uses2' in cssfile
    assert '.static_uses1' in cssfile
    assert 'url(http://localhost:8000/media/' in cssfile
    assert 'rf/planapp/page/media/img/uses1.gif' in cssfile
    
    assert '%s.js' % hash_js1 in content
    assert '%s.js' % hash_js2 in content
    assert 'planapp/page/media/js/static_uses1.js' not in content
    assert 'planapp/page/media/js/static_uses2.js' not in content

    assert '%s.css' % hash_css in content
    assert 'planapp/page/media/css/static_uses1.css' not in content
    assert 'planapp/page/media/css/static_uses2.css' not in content

    assert content.find('addon/dojo.js') < \
        content.find('%s.js' % hash_js1)
    assert content.find('%s.js' % hash_js1) < \
        content.find('media/uses1.js')

    assert content.find('media/uses1.css') < \
        content.find('%s.css' % hash_css)
    assert content.find('%s.css' % hash_css) < \
        content.find('site.com/handheld.css')

    assert content.find('js/ie7only.css') < \
        content.find('%s.js' % hash_js2)

@with_setup(setup, teardown)
def test_deploy_fewest():
    hash_css = '9ecd76d6b65856eb899846a6271a527a'
    hash_js = '323b64060e8403aa5b99796b3b5efdd9'

    settings.CRUNCHYFROG_PLANS = 'mediadeploy_fewest'

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    exist(
        'ff/%s.css' % hash_css,
        'ff/%s.js' % hash_js,
        'ff/planapp/page/media/css/gte_ie6only.css',
        'ff/planapp/page/media/img/uses1.gif',
        'ff/planapp/page/media/img/uses2.gif',
        'ff/planapp/page/media/js/Controller.js',
        'ff/planapp/page/media/js/duplicated.js',
        'ff/planapp/page/media/js/ie7only.js',
        'ff/planapp/page/media/js/inline.js',
        'ff/planapp/page/media/js/notreferenced.js',
        'ff/planapp/page/media/js/static.js',
        'ff/planapp/page/media/js/static_uses1.js',
        'ff/planapp/page/media/js/static_uses2.js',
        'ff/planapp/page/media/js/View.js',
    )

    jsfile = get_contents(
        os.path.join(cachedir, 'ff', '%s.js' % hash_js)
    )
    assert 'static_uses2' in jsfile
    assert 'static_uses1' in jsfile
    assert 'static=' in jsfile
    assert 'duplicated' in jsfile
    assert jsfile.find('duplicated=null') < \
        jsfile.find('dojo.provide("dojox.timing._base")')

    cssfile = get_contents(
        os.path.join(cachedir, 'ff', '%s.css' % hash_css)
    )

    assert '.static_uses2' in cssfile
    assert '.static_uses1' in cssfile
    assert '.static {' in cssfile

    assert '%s.js' % hash_js in content
    assert 'planapp/page/media/js/static' not in content
    assert 'planapp/page/media/js/duplicated' not in content

    assert '%s.css' % hash_css in content

    assert content.find('addon/dojo') < \
        content.find('%s.js' % hash_js)
    assert content.find('%s.js' % hash_js) < \
        content.find('media/uses1.js')

    assert content.find('media/uses1.css') < \
        content.find('%s.css' % hash_css)
    assert content.find('%s.css' % hash_css) < \
        content.find('site.com/handheld.css')

@with_setup(setup, teardown)
def test_deploy_fewest_instrumented():
    hash_js = '0b23534654c55bb791f2e1fdefd4cdbb'

    ribt.instrument_site(True)
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_fewest'

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    assert '%s.js' % hash_js in content

    jsfile = get_contents(
        os.path.join(cachedir, 'ff', '%s.js' % hash_js)
    )

    assert "dojo.provide('ribt')" in jsfile

    ribt.instrument_site(False)

@with_setup(setup, teardown)
def test_missing_rollup_requirement():
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_fewest'

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full_missing.yaml', c)

    py.test.raises(TemplateDoesNotExist, pa.dumps)

@with_setup(setup, teardown)
def test_deploy_reusable_unroll_updated():
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_reusable'

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    assert 'planapp/page/media/js/static_uses1.js' not in content

    sleep(1.0) 
    os.utime(loader.find_template_path('planapp/page/media/js/static_uses1.js'),
        None)

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    assert 'planapp/page/media/js/static_uses1.js' not in content

    plan_options(unroll_recently_modified=True)

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    assert 'planapp/page/media/js/static_uses1.js' in content

    sleep(1.0) 
    os.utime(loader.find_template_path('planapp/page/media/js/Controller.js'),
        None)

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    assert "dojo.require('PlanApp.Page.Controller');" in content

def test_deploy_reusable_no_js_minifying():
    raise SkipTest('')
