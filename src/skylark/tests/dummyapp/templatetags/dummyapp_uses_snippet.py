from django import template

from skylark.snippet import SnippetAssembly

register = template.Library()


@register.tag()
def tag_uses_snippet(parser, token):
    return TagUsesSnippetNode()


class TagUsesSnippetNode(template.Node):
    def render(self, context):
        sa = SnippetAssembly('dummyapp/snippet/snippet.yaml', context)

        return sa.dumps()
