from django import template
from django.template.loader import render_to_string
from crunchyfrog.renderer import add_yaml

register = template.Library()

@register.tag(name="dummy")
def do_overview(parser, token):
    return DummyTagNode()

class DummyTagNode(template.Node):
    @add_yaml('dummyapp/tag/tag.yaml')
    def render(self, context):
        return render_to_string("dummyapp/tag/tag.html", context_instance=context)
