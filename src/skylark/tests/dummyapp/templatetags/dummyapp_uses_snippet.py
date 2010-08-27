from django import template
from django.template.loader import render_to_string
from skylark.renderer import add_yaml
from skylark.snippet import SnippetAssembly, RequestContext

register = template.Library()

@register.tag()
def tag_uses_snippet(parser, token):
    return TagUsesSnippetNode()

class TagUsesSnippetNode(template.Node):
    def render(self, context):
        sa = SnippetAssembly('dummyapp/snippet/snippet.yaml', context)

        return sa.dumps()
