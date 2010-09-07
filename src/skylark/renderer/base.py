import copy
import os
import yaml

from django.template import Template, loader

from skylark import plans
from skylark.conf import settings
from skylark import chirp


class Renderer(object):
    """
    The base class that performs the heavy lifting of taking page instructions
    and rendering them into actual HTML.  This class is not meant to be used by
    itself but instead extended.  The template_name variables should contain
    the template that you wish to use to render whatever kind of page you need.
    In other words, check out Xhtml401Transitional for an example.
    """

    # Used to place a doctype at the beginning of a rendered page.  This only
    # applies to html and xhtml pages that are rendered with a PageAssembly.
    doctype = ('<!DOCTYPE html>')

    # What template do we use to render?
    template_name = 'skylark/html5.html'
    snippet_template_name = 'skylark/htmlsnippet.html'

    def __init__(self, page_instructions, context, render_full_page=True,
                 omit_media=False):
        self.page_instructions = page_instructions
        self.context = context
        self.render_full_page = render_full_page
        self.omit_media = omit_media

    def render(self):
        """
        Takes a chunk of page instructions and renders a page according to the
        rules found within

        This return a string representing the HTML or similar output
        """
        assert self.page_instructions.body, \
            'The body has not been specified in the page instructions ' + \
            '(body: in your yaml file)'

        if self.render_full_page:
            assert self.page_instructions.title, \
                'The title has not been specified in the page ' + \
                'instructions (title: in your yaml file)'

        plan = plans.get_for_context(self.context,
            self.page_instructions.render_full_page)
        prepared_instructions = plan.prepare(self.page_instructions,
            omit_media=self.omit_media)

        render_context = copy.copy(self.context)
        render_context['cache_url'] = settings.SKYLARK_CACHE_URL
        render_context['doctype'] = self.doctype
        render_context['prepared_instructions'] = prepared_instructions
        render_context['is_instrumented'] = chirp.is_instrumented()

        if self.render_full_page:
            t = self.template_name
        else:
            t = self.snippet_template_name
        self.template = loader.get_template(t)

        return self.template.render(render_context)
