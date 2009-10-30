import copy
import os
import shutil
import yaml
from django.template import Template, TemplateDoesNotExist, loader
from urlparse import urljoin
from crunchyfrog.conf import settings
from crunchyfrog.processor import clevercss

def add_yaml(yamlfile):
    """
    Template tag that can be used to add crunchy dependencies out side the normal PageAssembly
    """
    def render_yaml(yamlfile, page_instructions, context):
        source, origin = loader.find_template_source(yamlfile)
        sourcerendered = Template(source).render(context)

        instructions = yaml.load(sourcerendered)

        if 'uses' in instructions:
            uses = instructions['uses']

            for usesfile in uses:
                render_yaml(usesfile['file'], page_instructions, context)

        page_instructions.add(instructions, yamlfile)

    def process_yaml(func):
        def wrapper(*args, **kwargs):
            context = args[1]

            if context.has_key('__page_instructions'):
                page_instructions = context['__page_instructions']
                render_yaml(yamlfile, page_instructions, context)

            return func(*args, **kwargs)
        return wrapper

    return process_yaml

def process_clevercss(source):
    """
    This is part of the processing_funcs that Renderer will use to perform any
    special transformations or filtering on the output of a rendered template.

    This particular one uses CleverCSS to process a meta-css file and convert
    it into normal css.  More info at http://sandbox.pocoo.org/clevercss/
    """
    return clevercss.convert(source)

class Renderer(object):
    """
    The base class that performs the heavy lifting of taking page instructions
    and rendering them into actual HTML.  This class is not meant to be used by
    itself but instead extended.  The template_str class variables should
    contain the template that you wish to use to render whatever kind of page
    you need.  In other words, check out Xhtml401Transitional for an example.
    """
    template_str = None # This is the one that needs to be replaced in the sub class

    """
    These are a set of special functions that can be used to manipulate the
    source of the page.  The way these get triggered is through the attribute
    "process:" in the yaml file.  Here's a quick example.

        static: myapp/common.css
        process: clevercss

    As the instruction is parsed, we come across process and if it matches a
    defined processing_funcs we will provide the source of the page and allow
    it to be modified by the function.
    """
    processing_funcs = {
        'clevercss': process_clevercss
    }

    """
    Used to place a doctype at the beginning of a rendered page.  This only
    applies to html and xhtml pages that are rendered with a PageAssembly.
    """
    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'

    """
    What template do we use to render?
    """
    template_name = 'crunchyfrog/html401.html'
    snippet_template_name = 'crunchyfrog/htmlsnippet.html'

    def find_template_source(self, name, dirs=None):
        """
        This is a copy paste job from django.template.loader.

        The reason you find this here is that in DEBUG mode, Django will not
        return the origin, which is imporant to us since we are trying to mirror
        the directory structure and also copy some of the files inside of any media
        directory into the cache as well.

        So, we have to implement our own so that we are always able to determing
        the origin
        """
        # Calculate template_source_loaders the first time the function is executed
        # because putting this logic in the module-level namespace may cause
        # circular import errors. See Django ticket #1292.
        assert loader.template_source_loaders, 'The template loader has not initialized the template_source_loader, this is very unsual'

        for djangoloader in loader.template_source_loaders:
            try:
                source, display_name = djangoloader(name, dirs)
                origin = loader.LoaderOrigin(display_name, djangoloader, name, dirs)
                return (source, origin)
            except TemplateDoesNotExist:
                pass

        raise TemplateDoesNotExist, name

    def __init__(self, page_instructions, context, render_full_page=True):
        """
        cache_root is normally MEDIA_ROOT/cfcache but can be changed in
        your settings.py file
        """
        self.cache_root        = settings.CRUNCHYFROG_CACHE_ROOT
        """ Like cache_root, normally this is MEDIA_URL/cfcache """
        self.cache_url         = settings.CRUNCHYFROG_CACHE_URL
        self.page_instructions = page_instructions
        self.context           = context
        self.render_full_page  = render_full_page

        t = self.template_name if render_full_page else self.snippet_template_name
        self.template = loader.get_template(t)

        """
        As we process the page instructions, we gather the output we need to
        convert this into an html page inside this dictionary
        """
        self.prepared_instructions = {}

        if not os.path.exists(self.cache_root):
            os.makedirs(self.cache_root)

    def get_media_source(self, template_name, process_func=None, context=None):
        """
        Responsible for taking a template and generating the contents.

            * Renders the template with the given context if applicable
            * Passes it through the process function if provided
        """
        source, origin = self.find_template_source(template_name)

        if context:
            template = Template(source)
            source   = template.render(context)

        if process_func:
            source = process_func(source)

        return source

    def copy_to_media(self, template_name, process_func=None):
        """
        Part of our goal here is to make the placement of media a transparent deal.
        Django does not currently make this easy, you typically have to handle your
        media in a pretty manual fashion.

        This method takes a file that is somewhere in your template path (for
        example /blog/templates/blog/list/media/css/screen.css and copies it
        to the cache.  It ends up having the same directory structure, so in the
        end gets copied to MEDIA_ROOT/cfcache/blog/media/css/screen.css.

        """
        dirpath  = os.path.join(self.cache_root, os.path.dirname(template_name))
        filename = os.path.basename(template_name)
        fullpath = os.path.join(dirpath, filename)

        if settings.DEBUG:
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

            source, origin = self.find_template_source(template_name)

            source = self.get_media_source(template_name, process_func)

            f = open(fullpath, 'w')
            f.write(source)
            f.close()

        return urljoin(self.cache_url, template_name), filename

    def prepare_file(self, item_name, page_instructions):
        """
        This method takes lines from our YAML files and decides what to do with
        them.

        An example is::

            js:
                - url: http://somesite.com/somefile.html

            css:
                - static: blog/index/

        This method is a factored out version of prepare_css and prepare_js.
        """
        if not self.prepared_instructions.has_key(item_name):
            self.prepared_instructions[item_name] = []

        for instruction in getattr(page_instructions, item_name):
            if instruction.has_key('url'):
                self.prepared_instructions[item_name].append({ 'location': instruction['url'] })
            else:
                template_name = context = process_func = None

                if instruction.has_key('process') and Renderer.processing_funcs.has_key(instruction['process']):
                    process_func = Renderer.processing_funcs[instruction['process']]
                elif instruction.has_key('process'):
                    raise AttributeError('Could not find a process function matching %s, available ones are: %s' % 
                        (instruction['process'], ', '.join(Renderer.processing_funcs.keys()),))

                item = copy.copy(instruction)

                if instruction.has_key('static'):
                    template_name = instruction['static']
                    location, filename = self.copy_to_media(template_name, process_func)
                    item['location'] = location
                elif instruction.has_key('inline'):
                    template_name = instruction['inline']
                    context = self.context
                    source = self.get_media_source(template_name, process_func, context)
                    item['source'] = source

                assert template_name, 'You must provide either "static" or "inline" properties that point to a file, provided object was %r' % instruction

                if instruction.has_key('include') and not instruction['include']:
                    continue

                self.prepared_instructions[item_name].append(item)

    def prepare_assets(self, page_instructions, assets=None):
        """
        There are some special cases when working with css and javascript that
        we make allowances for.

        The first is css.  When you author your css it's normal to see
        references to images like this::

            background-image: url(../img/header/background.png)

        CSS authors are used to referencing images this way.  Since we cache css files
        from within the app to the MEDIA_ROOT, we need to also copy images that may be
        used.  We do this by looking for media/img relative to the yaml file that was
        used to generate the page instructions and copy this entire directory to the
        cache.

        The same thing goes for Javascript templates.  They are not a widely used
        item, but we've included them because it's part of what our original goal
        was when developing this app.

        You can put HTML files in media/js/templates and the entire templates directory
        will be copied into the MEDIA_ROOT in the appropriate spot.  This way your
        javascript files can utilize them without having to worry about where they are.

        This method will work with directories that are relative to the YAML
        file or the app's templates directory.  The following will essentially
        copy the same directory to the cache:

            self.prepare_assets(pi, ('media/js',))
            self.prepare_assets(pi, ('blog/list/media/js',))

        """
        assert type(assets) == tuple or type(assets) == list

        for yaml in page_instructions.yaml:
            # yaml = app/page/page.yaml
            source, origin = self.find_template_source(yaml)
            del source # we don't need it
            origin = str(origin)

            yaml_basedir = os.path.dirname(yaml) # should give us app/page
            template_basedir = origin[:origin.find(yaml)]

            for directory in assets:
                if not yaml_basedir in directory:
                    directory = os.path.join(yaml_basedir, directory)

                sourcedirectory = os.path.join(template_basedir, directory)

                if not os.path.isdir(sourcedirectory): continue

                cachedirectory = os.path.join(self.cache_root, directory)

                if os.path.isdir(cachedirectory):
                    if self.assets_are_stale(sourcedirectory, cachedirectory):
                        shutil.rmtree(cachedirectory)
                    else:
                        continue

                shutil.copytree(sourcedirectory, cachedirectory)

    def assets_are_stale(self, sourcedirectory, cachedirectory):
        """
        Looks through the source files for either media/img or media/js/templates
        and determines if the cache is stale
        """
        cache_age = os.path.getmtime(cachedirectory)

        for path in os.walk(sourcedirectory):
            for file in path[2]:
                if os.path.getmtime(os.path.join(path[0], file)) > cache_age:
                    return True

        return False

    def prepare_js(self, page_instructions):
        """
        Processes the js section of the page instructions
        """
        if hasattr(page_instructions, 'js'):
            self.prepare_assets(page_instructions, ('media/js/templates',))

        self.prepare_file('js', page_instructions)

    def prepare_css(self, page_instructions):
        """
        Processes the css section
        """
        if hasattr(page_instructions, 'css'):
            self.prepare_assets(page_instructions, ('media/img',))

        self.prepare_file('css', page_instructions)

    def prepare_title(self, page_instructions):
        """
        Prepares the title for the page
        """
        template = Template(page_instructions.title)
        self.prepared_instructions['title'] = unicode(template.render(self.context))

    def prepare_body(self, page_instructions):
        """
        Takes the body section and renders it, storing it in prepared_instructions
        """
        template = loader.get_template(page_instructions.body)
        self.context['__page_instructions'] = page_instructions
        self.prepared_instructions['body'] = unicode(template.render(self.context))

    def prepare_meta(self, page_instructions):
        """
        Prepares the meta section
        """
        self.prepared_instructions['meta'] = page_instructions.meta

    def prepare_dojo(self, page_instructions):
        dojo = page_instructions.dojo

        self.prepared_instructions['dojo'] = dojo

        for dojo_module in dojo:
            assert 'namespace' in dojo_module, ('You are missing the '
                'namespace attribute for this item')
            assert 'location' in dojo_module, ('You are missing the '
                 'location attribute for this item')
            assert 'require' in dojo_module, ('You are missing the '
                 'require list for this item')

            namespace = dojo_module['namespace']
            location = dojo_module['location']
            require = dojo_module['require']

            """
            We're going to copy all the files that are in this directory to the
            cache.  This is not ideal, as not all the files may be used but the
            alternative is we ask the user specifically which ones they need.
            Since this is within the context of Dojo, that may not make the most
            sense.
            """
            self.prepare_assets(page_instructions, (location,))

    def render(self):
        """
        Takes a chunk of page instructions and renders a page according to the rules
        found within

        This return a string representing the HTML or similar output
        """
        assert self.page_instructions.body, 'The body has not been specified in the page instructions (body: in your yaml file)'

        if self.render_full_page:
            assert self.page_instructions.title, 'The title has not been specified in the page instructions (title: in your yaml file)'

        prep_pi = self.prepared_instructions
        raw_pi = self.page_instructions

        prep_pi['render_full_page'] = raw_pi.render_full_page

        self.prepare_title(raw_pi)
        self.prepare_body(raw_pi)
        self.prepare_js(raw_pi)
        self.prepare_css(raw_pi)
        self.prepare_meta(raw_pi)
        self.prepare_dojo(raw_pi)

        render_context = copy.copy(self.context)
        render_context['cache_url'] = settings.CRUNCHYFROG_CACHE_URL
        render_context['doctype'] = self.doctype
        render_context['prepared_instructions'] = prep_pi

        return self.template.render(render_context)
