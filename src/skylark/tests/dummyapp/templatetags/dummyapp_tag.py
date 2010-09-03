from django import template
from django.template.loader import render_to_string
from skylark.snippet import SnippetAssembly

register = template.Library()


@register.tag
def dummy(parser, token):
    return DummyTagNode()


class DummyTagNode(template.Node):
    def render(self, context):
        sa = SnippetAssembly("dummyapp/tag/tag.yaml", context)
        return sa.dumps()
