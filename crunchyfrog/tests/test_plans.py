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
    hash_js2 = '1ce89799dfc95d689dbba2f39ff84cc5'
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
    assert jsfile.find("dojo.registerModulePath('RibtTools'") < \
        jsfile.find("dojo.provide('RibtTools.Error')")
    assert "dojo.registerModulePath('RibtTools" not in content

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
    hash_js = '75af0fd1dd1e4ff42eb5af467cd7619d'

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
    hash_js = '8b08654e90ffc3676f34c843395cd53c'

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
def test_deploy_unroll_updated():
    def render_full():
        request = get_request_fixture()
        c = RequestContext(request)
        pa = PageAssembly('planapp/page/full.yaml', c)

        return pa.dumps()

    time_newer = (time_started() + 10, time_started() + 10,)
    time_older = (time_started() - 1000, time_started() - 1000,)

    def make_them(to_time):
        os.utime(loader.find_template_path('planapp/page/media/js/static_uses1.js'),
            to_time)
        os.utime(loader.find_template_path('planapp/page/media/js/Controller.js'),
            to_time)

    # Check both plans, they should behave the same here
    for cfplan_setting in ('mediadeploy_reusable', 'mediadeploy_fewest',):
        # Let's make them older than when CF started
        make_them(time_older)
        plan_options(unroll_recently_modified=False)

        settings.CRUNCHYFROG_PLANS = cfplan_setting

        content = render_full()

        # Both of these should be rolled up
        assert 'planapp/page/media/js/static_uses1.js' not in content
        assert "dojo.require('PlanApp.Page.Controller');" not in content

        # Now let's fake modify our files
        #sleep(1.0) 
        make_them(time_newer)

        content = render_full()

        # We haven't told our plan to unroll anything, they should still be
        # rolled up
        assert 'planapp/page/media/js/static_uses1.js' not in content
        assert "dojo.require('PlanApp.Page.Controller');" not in content

        # Now, we'll tell our plan to unroll recently modified
        plan_options(unroll_recently_modified=True)

        content = render_full()

        # This should still unrolled, we don't unroll static JS
        assert 'planapp/page/media/js/static_uses1.js' not in content
        # And this should be unrolled now
        assert "dojo.require('PlanApp.Page.Controller');" in content

@with_setup(setup, teardown)
def test_deploy_reusable_no_js_minifying():
    hash_js = '3dd295714e3ad47c9212dd7a2f6a1a7d'

    settings.CRUNCHYFROG_PLANS = 'mediadeploy_reusable'

    plan_options(minify_javascript=False)

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    jsfile = get_contents(
        os.path.join(cachedir, 'rf', '%s.js' % hash_js)
    )

    assert '\n        ' in jsfile
    assert '//' in jsfile
    # Should be Dojo documentation in here
    assert '// summary:' in jsfile

@with_setup(setup, teardown)
def test_will_not_needlessly_rollup():
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_reusable'

    hash_js1 = '3dd295714e3ad47c9212dd7a2f6a1a7d'
    filename = os.path.join(cachedir, 'rf', '%s.js' % hash_js1)

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    first_time = os.stat(filename).st_mtime
    first_listing = os.listdir(os.path.join(cachedir, 'rf'))

    sleep(1.0) 

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    assert first_time == os.stat(filename).st_mtime
    assert first_listing == os.listdir(os.path.join(cachedir, 'rf'))
