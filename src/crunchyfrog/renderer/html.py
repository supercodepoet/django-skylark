from crunchyfrog.renderer import Renderer

class Html401Strict(Renderer):
    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Strict//EN" "http://www.w3.org/TR/html4/strict.dtd">'
    template_name = 'crunchyfrog/html401.html'
    snippet_template_name = 'crunchyfrog/htmlsnippet.html'

class Html401Transitional(Renderer):
    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'
    template_name = 'crunchyfrog/html401.html'
    snippet_template_name = 'crunchyfrog/htmlsnippet.html'

class Html401Frameset(Renderer):
    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">'
    template_name = 'crunchyfrog/html401.html'
    snippet_template_name = 'crunchyfrog/htmlsnippet.html'
