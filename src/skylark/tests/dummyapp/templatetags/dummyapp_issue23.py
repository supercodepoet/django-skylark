from django import template

from skylark.snippet import SnippetAssembly

register = template.Library()


@register.tag
def tt_snippet_assembly(parser, token):
    return TtSnippetAssemblyNode()


class TtSnippetAssemblyNode(template.Node):
    def render(self, context):
        sa = SnippetAssembly("dummyapp/issue_bb_23/tt_sa.yaml", context)
        return sa.dumps();


@register.tag
def tt_after_snippet_assembly(parser, token):
    return TtAfterSnippetAssemblyNode()


class TtAfterSnippetAssemblyNode(template.Node):
    def render(self, context):
        sa = SnippetAssembly("dummyapp/issue_bb_23/tt_after_sa.yaml", context)
        return sa.dumps();
