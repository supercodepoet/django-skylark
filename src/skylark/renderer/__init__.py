from skylark.renderer.base import Renderer
from skylark.renderer.html import *
from skylark.renderer.xhtml import *

renderers = {
    'html': Html5,
    'HTML 4.01 Transitional': Html401Transitional,
    'HTML 4.01 Strict': Html401Strict,
    'HTML 4.01 Frameset':Html401Frameset,
    'XHTML 1.0 Transitional': Xhtml1Transitional,
    'XHTML 1.0 Strict': Xhtml1Strict,
    'XHTML 1.0 Frameset': Xhtml1Frameset,
}
    

def get(doctype, instructions, context, **kwargs):
    return renderers[str(doctype)](
        instructions, context, **kwargs)
