from skylark.renderer import Renderer


class Html5(Renderer):
    doctype = '<!DOCTYPE html>'
    template_name = 'skylark/html5.html'
    snippet_template_name = 'skylark/htmlsnippet.html'


class Html401Strict(Renderer):
    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Strict//EN" "http://www.w3.org/TR/html4/strict.dtd">'
    template_name = 'skylark/html401.html'
    snippet_template_name = 'skylark/htmlsnippet.html'


class Html401Transitional(Renderer):
    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'
    template_name = 'skylark/html401.html'
    snippet_template_name = 'skylark/htmlsnippet.html'


class Html401Frameset(Renderer):
    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">'
    template_name = 'skylark/html401.html'
    snippet_template_name = 'skylark/htmlsnippet.html'
