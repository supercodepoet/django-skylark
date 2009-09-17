from crunchyfrog.renderer import Renderer

xhtmltemplate = """
<html>
    <head>
        <title>{{ prepared_instructions.title|safe }}</title>
    {% for meta in prepared_instructions.meta %}
        <meta {{ meta.key|default:"name" }}="{{ meta.name }}" content="{{ meta.content }}" />
    {% endfor %}
    {% for css in prepared_instructions.css %}
        {% if css.ieversion %}
        <!--[if {{ css.ieversion }}]>
        {% endif %}
        <link rel="stylesheet" type="text/css" href="{{ css.location }}" media="{{ css.media|default:"screen" }}" />
        {% if css.ieversion %}
        <![endif]-->
        {% endif %}
    {% endfor %}
    <script type="text/javascript">
        //<![CDATA[
        // Injected by Django CrunchyFrog
        var $CF = { MEDIA_URL: "{{ cache_url }}" }
        //]]>
    </script>
    {% for js in prepared_instructions.js %}
        <script type="text/javascript" src="{{ js.location }}"></script>
    {% endfor %}
    </head>
    {% autoescape off %}
        {{ prepared_instructions.body }}
    {% endautoescape %}
</html>"""

class Xhtml1Strict(Renderer):
    def __init__(self, page_instructions, context):
        super(Xhtml1Strict, self).__init__(page_instructions, context)
    template_str = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">' + xhtmltemplate

class Xhtml1Transitional(Renderer):
    def __init__(self, page_instructions, context):
        super(Xhtml1Transitional, self).__init__(page_instructions, context)
    template_str = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/xhtml1-loose.dtd">' + xhtmltemplate

class Xhtml1Frameset(Renderer):
    def __init__(self, page_instructions, context):
        super(Xhtml1Frameset, self).__init__(page_instructions, context)
    template_str = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/xhtml1-frameset.dtd">' + xhtmltemplate
