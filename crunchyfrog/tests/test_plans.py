import py.test
import os

from nose.tools import with_setup
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from crunchyfrog import *
from crunchyfrog.page import PageAssembly
from crunchyfrog.plans import get_for_context, MissingMediaPlan
from crunchyfrog.plans import SeparateEverything, FewestFiles

from crunchyfrog.tests import *

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

    old_debug = settings.DEBUG
    settings.DEBUG = False
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_notthere'
    py.test.raises(MissingMediaPlan, get_for_context, context, render_full_page)
    settings.DEBUG = old_debug

@with_setup(setup, teardown)
@attr('focus')
def test_deploy_reusable():
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_reusable'

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    jsfile = get_contents(
        os.path.join(cachedir, 'rf', '2c4566e48a3bdf73eddd5a56072fbc71.js')
    )
    assert 'var static_uses2=null;var static_uses1=null;' in jsfile

    cssfile = get_contents(
        os.path.join(cachedir, 'rf', 'ee184e5fad8366ee655a090043693c30.css')
    )
    assert '.static_uses2' in cssfile
    assert '.static_uses1' in cssfile
    assert 'url(http://localhost:8000/media/' in cssfile
    assert 'rf/planapp/page/media/img/uses1.gif' in cssfile
    
    assert '2c4566e48a3bdf73eddd5a56072fbc71.js' in content
    assert 'planapp/page/media/js/static_uses1.js' not in content
    assert 'planapp/page/media/js/static_uses2.js' not in content

    assert 'ee184e5fad8366ee655a090043693c30.css' in content
    assert 'planapp/page/media/css/static_uses1.css' not in content
    assert 'planapp/page/media/css/static_uses2.css' not in content

    assert content.find('media/uses2.js') < \
        content.find('2c4566e48a3bdf73eddd5a56072fbc71.js')
    assert content.find('2c4566e48a3bdf73eddd5a56072fbc71.js') < \
        content.find('media/uses1.js')

    assert content.find('media/uses1.css') < \
        content.find('ee184e5fad8366ee655a090043693c30.css')
    assert content.find('ee184e5fad8366ee655a090043693c30.css') < \
        content.find('site.com/handheld.css')

@with_setup(setup, teardown)
@attr('focus')
def test_deploy_reusable():
    settings.CRUNCHYFROG_PLANS = 'mediadeploy_fewest'

    request = get_request_fixture()
    c = RequestContext(request)
    pa = PageAssembly('planapp/page/full.yaml', c)

    content = pa.dumps()

    jsfile = get_contents(
        os.path.join(cachedir, 'ff', 'f87385fc7d0a0eef92c19a7110966425.js')
    )
    assert 'static_uses2' in jsfile
    assert 'static_uses1' in jsfile
    assert 'static=' in jsfile
    assert 'duplicated' in jsfile

    cssfile = get_contents(
        os.path.join(cachedir, 'ff', '9ecd76d6b65856eb899846a6271a527a.css')
    )

    assert '.static_uses2' in cssfile
    assert '.static_uses1' in cssfile
    assert '.static {' in cssfile

    assert 'f87385fc7d0a0eef92c19a7110966425.js' in content
    assert 'planapp/page/media/js/static' not in content
    assert 'planapp/page/media/js/duplicated' not in content

    assert '9ecd76d6b65856eb899846a6271a527a.css' in content

    assert content.find('media/uses2.js') < \
        content.find('f87385fc7d0a0eef92c19a7110966425.js')
    assert content.find('f87385fc7d0a0eef92c19a7110966425.js') < \
        content.find('media/uses1.js')

    assert content.find('media/uses1.css') < \
        content.find('9ecd76d6b65856eb899846a6271a527a.css')
    assert content.find('9ecd76d6b65856eb899846a6271a527a.css') < \
        content.find('site.com/handheld.css')
