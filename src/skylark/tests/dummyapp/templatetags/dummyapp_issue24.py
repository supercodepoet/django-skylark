from django import template
from django.template.loader import render_to_string

from skylark.snippet import SnippetAssembly, RequestContext

register = template.Library()

@register.tag
def snippet_assembly(parser, token):
    return SnippetAssemblyNode()

class SnippetAssemblyNode(template.Node):
    def render(self, context):
        sa = SnippetAssembly("dummyapp/issue24/sa.yaml", context)
        return sa.dumps();
