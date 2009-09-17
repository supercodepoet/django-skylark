from crunchyfrog.renderer import Renderer

htmltemplate = """
<html>
    <head>
        <title>{{ prepared_instructions.title|safe }}</title>
    {% for meta in prepared_instructions.meta %}
        <meta {{ meta.key|default:"name" }}="{{ meta.name }}" content="{{ meta.content }}">
    {% endfor %}
    {% for css in prepared_instructions.css %}
        {% if css.ieversion %}
        <!--[if {{ css.ieversion }}]>
        {% endif %}
        <link rel="stylesheet" type="text/css" href="{{ css.location }}" media="{{ css.media|default:"screen" }}">
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

class Html401Strict(Renderer):
    def __init__(self, page_instructions, context):
        super(Html401Strict, self).__init__(page_instructions, context)
    template_str = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Strict//EN" "http://www.w3.org/TR/html4/strict.dtd">' + htmltemplate

class Html401Transitional(Renderer):
    def __init__(self, page_instructions, context):
        super(Html401Transitional, self).__init__(page_instructions, context)
    template_str = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">' + htmltemplate

class Html401Frameset(Renderer):
    def __init__(self, page_instructions, context):
        super(Html401Frameset, self).__init__(page_instructions, context)
    template_str = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">' + htmltemplate
