from django import template
from django.template.loader import render_to_string

from crunchyfrog.renderer import add_yaml
from crunchyfrog.snippet import SnippetAssembly, RequestContext

register = template.Library()

@register.tag(name="tt_snippet_assembly")
def do_overview(parser, token):
    return TtSnippetAssembly()

class TtSnippetAssembly(template.Node):
    @add_yaml('dummyapp/issue23/tt_sa.yaml')
    def render(self, context):
        sa = SnippetAssembly("dummyapp/issue23/tt_sa.yaml", context)
        return sa.dumps();

@register.tag(name="tt_after_snippet_assembly")
def do_overview(parser, token):
    return TtAfterSnippetAssembly()

class TtAfterSnippetAssembly(template.Node):
    @add_yaml('dummyapp/issue23/tt_after_sa.yaml')
    def render(self, context):
        return render_to_string("dummyapp/issue23/tt_after_sa.html", context_instance=context)
