import py.test
import yaml

from nose.tools import with_setup
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from django import template
from crunchyfrog.instructions import PageInstructions
from crunchyfrog.tests import *

def get_object(file):
    source, origin = template.loader.find_template_source(file)
    assert source, 'The template loader found the template but it is completely empty'

    context = template.Context()
    sourcerendered = template.Template(source).render(context)
    assert sourcerendered, 'yamlfile needs to contain something'

    return yaml.load(sourcerendered)

obj = get_object('planapp/page/full.yaml')
fpi = PageInstructions()
fpi.add(obj, 'planapp/page/full.yaml')

def test_filter_only_uses():
    global fpi
    filtered = fpi.filter(only_uses=True)

    jsfiles = set([ i['sourcefile'] for i in filtered.js ])
    assert jsfiles == set(
        ['planapp/page/uses1.yaml', 'planapp/page/uses2.yaml'])

    cssfiles = set([ i['sourcefile'] for i in filtered.css ])
    assert cssfiles == set([])

def test_filter_exclude_uses():
    global fpi
    filtered = fpi.filter(exclude_uses=True)

    jsfiles = set([ i['sourcefile'] for i in filtered.js ])
    assert jsfiles == set(['planapp/page/full.yaml'])

    cssfiles = set([ i['sourcefile'] for i in filtered.css ])
    assert cssfiles == set(['planapp/page/full.yaml'])
