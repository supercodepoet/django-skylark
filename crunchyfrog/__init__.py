import hashlib
import renderer
import yaml
from django import http, template
from django.core.cache import cache
from django.core.urlresolvers import resolve
from crunchyfrog.conf import settings
from crunchyfrog.instructions import PageInstructions

class HttpResponse(http.HttpResponse):
    """
    Essentially, a copy of Django's version.  We are making our own here in anticipation
    of some additional features in the future.
    """
    def __init__(self, content='', mimetype=None, status=None,
            content_type=None):
        super(HttpResponse, self).__init__(content, mimetype, status, content_type)

class RequestContext(template.RequestContext):
    """
    Adds the raw request to the object, we need this to perform some caching work
    later on
    """
    def __init__(self, request, dict=None, processors=None):
        super(RequestContext, self).__init__(request, dict, processors)
        self.request = request

class BaseAssembly(object):
    """
    Overview
    --------
    Provides a way to specify a minimal set of instructions inside of a YAML file
    that get rendered to an HTML page.

    * You don't have to worry about <html> or <head> sections of your page
    * You don't have to craft <script> or <style> tags
    * You can reference any file as if it were a Dango template
    * You can combine YAML page instructions to make things modular
    * CleverCSS is built-in
    * and more to come

    The goal of this is to make web development quicker by eliminating some of the
    repated hastle of setting up HTML, CSS, images, and javascript.

    Basic usage:
    ------------

    Make a YAML file called blog/list/list.yaml::

        page: blog/list/list.html
        title: My Blog

    Make blog/list/list.html::

        <body>
            <h1>Hello {{ what }}</h1>
        </body>

    Create a Django view like this::
        from django.http import HttpResponse
        from crunchyfrog.page import PageAssembly, RequestContext

        def list(request):
            c = RequestContext(request, {
                'what': 'World'
            })

            pa = PageAssembly('blog/list/list.yaml', c)

            return pa.get_http_response()

    And behold the complete HTML page produced
    """
    def __init__(self, yamlfiles, context, cache_key = None, use_cache = True):
        assert hasattr(self, 'render_full_page'), ('You must set render_full_page to True '
            'or False on the subclass of BaseAssembly')
        assert isinstance(context, RequestContext), '%r must be of type RequestContext, you provided %s' % (context, type(context), )
        assert yamlfiles, '%r argument must not be empty or None' % (yamlfiles, )
        assert len(yamlfiles) != 0, '%r must not be zero length' % (yamlfiles, )

        self.use_cache = use_cache

        if self.use_cache:
            md5 = hashlib.md5()

            md5.update(context.request.get_host())

            if cache_key:
                md5.update(str(cache_key))
            else:
                view, args, kwargs = resolve(context.request.path)
                md5.update(view.__name__)

            self.cache_key = "crunchy_frog::page_instructions::%s" % (md5.hexdigest(),)

        """
        We can get the yamlfiles as a single string or a tuple, but by the time
        we set our instance variable it needs to be normalized to a tuple.

        In other words, this needs to happen:
            'some/file.yaml'   -->  ('some/file.yaml')
        """
        if isinstance(yamlfiles, str):
            yamlfiles = (yamlfiles,)

        self.yamlfiles = yamlfiles

        """
        It's important for our context to have the media root and url included,
        if it's not there we are going to add it
        """
        for var in ('MEDIA_ROOT', 'MEDIA_URL'):
            if not hasattr(context, var):
                context[var] = getattr(settings, var)

        self.context = context

    def __get_page_instructions(self):
        """
        Combines all the files and instructions into one object
        """
        page_instructions = PageInstructions()

        tried = []

        for file in self.yamlfiles:
            self.__add_page_instructions(page_instructions, file)

        if settings.CACHE_BACKEND and not settings.DEBUG:
            cache.set(self.cache_key, page_instructions, 86400)

        return page_instructions

    def __add_page_instructions(self, page_instructions, file):
        source, origin = template.loader.find_template_source(file)
        assert source, 'The template loader found the template but it is completely empty'

        sourcerendered = template.Template(source).render(self.context)
        assert sourcerendered, 'yamlfile needs to contain something'

        instructions = yaml.load(sourcerendered)

        if 'uses' in instructions:
            """
            We look for the uses section inside the YAML file, this is how
            we extend or reference other YAML files so we can factor out common things
            like javascript libraries, common css, or whatever else.

            This recursion places the "used" YAML file in front of the on we are
            currently processing.  Which makes the most sense.  You want you common
            libraries to come before the page specific ones.
            """
            uses = instructions['uses']

            for usesfile in uses:
                self.__add_page_instructions(page_instructions, usesfile['file'])

        page_instructions.add(instructions, file)

    def dumps(self):
        """
        Renders the page based on the page instructions, returning a string
        """
        if settings.CACHE_BACKEND and not settings.DEBUG:
            instructions = cache.get(self.cache_key)

            if not instructions:
                instructions = self.__get_page_instructions()

        else:
            instructions = self.__get_page_instructions()

        doctype = instructions.doctype or 'HTML 4.01 Transitional'

        page_renderer = renderer.get(doctype, instructions, self.context,
                                     self.render_full_page)

        return page_renderer.render()

    def get_http_response(self):
        """
        Returns an HttpResponse object will all the combined goodness
        """
        return HttpResponse(self.dumps())
