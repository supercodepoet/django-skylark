from skylark.renderer import Renderer


class Xhtml1Strict(Renderer):
    doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
    template_name = 'skylark/xhtml1.html'
    snippet_template_name = 'skylark/xhtmlsnippet.html'


class Xhtml1Transitional(Renderer):
    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/xhtml1-loose.dtd">'
    template_name = 'skylark/xhtml1.html'
    snippet_template_name = 'skylark/xhtmlsnippet.html'


class Xhtml1Frameset(Renderer):
    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/xhtml1-frameset.dtd">'
    template_name = 'skylark/xhtml1.html'
    snippet_template_name = 'skylark/xhtmlsnippet.html'
