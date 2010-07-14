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
from crunchyfrog.plans.base import BadOption, BadPlanSituation
from crunchyfrog.plans.separate import SeparateEverything
from crunchyfrog.plans.fewest import FewestFiles

from crunchyfrog.tests import *

def test_plan_options_invalid():
    py.test.raises(BadOption, plan_options, not_a_valid_option=True)

@with_setup(setup, teardown)
def test_can_change_deploy_plan_name():
    context = {}
    render_full_page = True

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

    # If we aren't rendering a full page, it should be SeparateEverything
    plan = get_for_context(context, False)
    assert isinstance(plan, SeparateEverything)

    settings.CRUNCHYFROG_PLANS = 'mediadeploy_bad'
    settings.CRUNCHYFROG_PLANS_DEFAULT = 'default'
    py.test.raises(ValueError, get_for_context, context, render_full_page)

    settings.DEBUG = False
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_notthere'
    py.test.raises(MissingMediaPlan, get_for_context, context, render_full_page)

@with_setup(setup, teardown)
def test_deploy_reusable():
    hash_js1 = '93be07cfe9c81198bb4c549c868ff731'
    hash_js2 = '48910f6a5624903b57466381e5c44daf'
    hash_css = 'ee184e5fad8366ee655a090043693c30'

    settings.DEBUG = False
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_reusable'

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    jsfile = get_contents(
        os.path.join(cachedir, 'out', '%s.js' % hash_js1)
    )
    assert 'var static_uses2=null;var static_uses1=null;' in jsfile

    jsfile = get_contents(
        os.path.join(cachedir, 'out', '%s.js' % hash_js2)
    )
    assert jsfile.find('dojo.provide("dojox.timing._base")') < \
        jsfile.find('dojo.provide("dojox.timing")')
    assert jsfile.find("dojo.provide('PlanApp.Page.View')") < \
        jsfile.find("dojo.provide('PlanApp.Page.Controller')")
    assert jsfile.find("dojo.registerModulePath('RibtTools'") < \
        jsfile.find("dojo.provide('RibtTools.Error')")
    assert "dojo.registerModulePath('RibtTools" not in content

    cssfile = get_contents(
        os.path.join(cachedir, 'out', '%s.css' % hash_css)
    )
    assert '.static_uses2' in cssfile
    assert '.static_uses1' in cssfile
    assert 'url(http://localhost:8000/media/' in cssfile
    assert 'out/planapp/page/media/img/uses1.gif' in cssfile
    
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
    hash_js = 'f839268d652274ab20d813c12ec47079'

    settings.CRUNCHYFROG_PLANS = 'mediadeploy_fewest'

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    exist(
        'out/%s.css' % hash_css,
        'out/%s.js' % hash_js,
        'out/planapp/page/media/css/gte_ie6only.css',
        'out/planapp/page/media/img/uses1.gif',
        'out/planapp/page/media/img/uses2.gif',
        'out/planapp/page/media/js/Controller.js',
        'out/planapp/page/media/js/duplicated.js',
        'out/planapp/page/media/js/ie7only.js',
        'out/planapp/page/media/js/inline.js',
        'out/planapp/page/media/js/notreferenced.js',
        'out/planapp/page/media/js/static.js',
        'out/planapp/page/media/js/static_uses1.js',
        'out/planapp/page/media/js/static_uses2.js',
        'out/planapp/page/media/js/View.js',
    )

    jsfile = get_contents(
        os.path.join(cachedir, 'out', '%s.js' % hash_js)
    )
    assert 'static_uses2' in jsfile
    assert 'static_uses1' in jsfile
    assert 'static=' in jsfile
    assert 'duplicated' in jsfile
    assert jsfile.find('duplicated=null') < \
        jsfile.find('dojo.provide("dojox.timing._base")')

    cssfile = get_contents(
        os.path.join(cachedir, 'out', '%s.css' % hash_css)
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
    hash_js = 'f2e1963891fcc6c815b966a436e46ba2'

    ribt.instrument_site(True)
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_fewest'

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    assert '%s.js' % hash_js in content

    jsfile = get_contents(
        os.path.join(cachedir, 'out', '%s.js' % hash_js)
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
def test_deploy_reusable_no_js_minifying():
    hash_js = '48910f6a5624903b57466381e5c44daf'

    settings.CRUNCHYFROG_PLANS = 'mediadeploy_reusable'

    plan_options(minify_javascript=False)

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    jsfile = get_contents(
        os.path.join(cachedir, 'out', '%s.js' % hash_js)
    )

    assert '\n        ' in jsfile
    assert '//' in jsfile
    # Should be Dojo documentation in here
    assert '// summary:' in jsfile

@with_setup(setup, teardown)
def test_will_not_needlessly_rollup():
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_reusable'

    hash_js1 = '48910f6a5624903b57466381e5c44daf'
    filename = os.path.join(cachedir, 'out', '%s.js' % hash_js1)

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    first_time = os.stat(filename).st_mtime
    first_listing = os.listdir(os.path.join(cachedir, 'out'))

    sleep(1.0) 

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    assert first_time == os.stat(filename).st_mtime
    assert first_listing == os.listdir(os.path.join(cachedir, 'out'))
