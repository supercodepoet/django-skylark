import copy
import os
import re
import filecmp
import shutil
import yaml
import hashlib
import pickle
import cssutils
import functools
import urllib
import logging
from urlparse import urljoin
from collections import deque

from django.template import Template, TemplateDoesNotExist
from django.template import loader as djangoloader
from django.utils.functional import memoize
from crunchyfrog.conf import settings
from crunchyfrog.processor import clevercss
from crunchyfrog import loader as cfloader
from crunchyfrog import ribt, time_started

class CssFormatError(Exception):
    pass
        
class BadOption(Exception):
    pass

class DojoModuleResolution(Exception):
    pass

class CssUtilsLoggingHandler(logging.Handler):
    _records = []
    def emit(self, record):
        if 'CSSStyleRule' in record.msg:
            self._records.append(record)

    def get_errors(self):
        records = self._records
        self._records = []
        return records

cssutils_handler = CssUtilsLoggingHandler()
__log = logging.getLogger('CssUtilsLogging')
__log.addHandler(cssutils_handler)
__log.setLevel(logging.ERROR)
cssutils.log.setLog(__log)

def find_directory_from_loader(page_instructions, asset):
    from django.template.loaders.app_directories import app_template_dirs
    template_dirs = list(settings.TEMPLATE_DIRS) + list(app_template_dirs)

    for dir in template_dirs:
        asset_dir = os.path.join(dir, asset)
        if os.path.isdir(asset_dir):
            return asset_dir

    raise TemplateDoesNotExist, ('Unable to find a directory within known '
        'template directories: %s' % asset)

def process_clevercss(source):
    """
    This is part of the processing_funcs that Renderer will use to perform any
    special transformations or filtering on the output of a rendered template.

    This particular one uses CleverCSS to process a meta-css file and convert
    it into normal css.  More info at http://sandbox.pocoo.org/clevercss/
    """
    return clevercss.convert(source)

class BasePlan(object):
    """
    Base class that all the plans can subclass.  It provides common things like
    copying directories, and other fancy pants things like that.
    """

    __media_source_cache = {}

    options = {
        'unroll_recently_modified': False,
        'minify_javascript': True,
    }

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

    make_css_urls_absolute = False

    cache_prefix = None

    def __init__(self, context, render_full_page):
        self._prepare_assets_cache = {}
        setattr(self, '_prepare_assets', memoize(
            self._prepare_assets, self._prepare_assets_cache, 2))

        self.cache_root = os.path.join(
            settings.CRUNCHYFROG_CACHE_ROOT, self.cache_prefix)
        self.cache_url = urljoin(settings.CRUNCHYFROG_CACHE_URL, '%s/' % self.cache_prefix)
        self.context = context
        self.render_full_page = render_full_page

        """
        As we process the page instructions, we gather the output we need to
        convert this into an html page inside this dictionary
        """
        self.prepared_instructions = {}
        self.prepared_instructions['render_full_page'] = self.render_full_page
        self.prepared_instructions['cache_prefix'] = '%s/' % self.cache_prefix

        if not os.path.exists(self.cache_root):
            os.makedirs(self.cache_root)

    @classmethod
    def set_options(*args, **kwargs):
        """
        Various options for how the plans behave
        """
        for option in kwargs:
            if option not in BasePlan.options:
                raise BadOption('%s is not a valid, must be a combination '
                    'of %s' % (option, ','.join(BasePlan.options.keys(),)))
        BasePlan.options.update(kwargs)

    def _get_media_stat(self, template_name):
        """
        Performs a os.stat on template_name, raising TemplatePathDoesNotExist
        if the template_name is not file based.
        """
        try:
            path = cfloader.find_template_path(template_name)
            return os.stat(path)
        except cfloader.TemplatePathDoesNotExist:
            return None

    def _get_media_source(self, template_name, process_func=None, context=None):
        """
        Responsible for taking a template and generating the contents.

            * Renders the template with the given context if applicable
            * Passes it through the process function if provided
        """
        cache = self.__media_source_cache

        mem_args = (template_name, process_func)
        if mem_args in cache and not context and not settings.DEBUG:
            source = cache[mem_args]
            is_cached = True
        else:
            source, origin = cfloader.find_template_source(template_name)

            if context:
                template = Template(source)
                return template.render(context), False

            if process_func:
                source = process_func(source)

            cache[mem_args] = source
            is_cached = False

        return source, is_cached

    def _copy_to_media(self, template_name, source=''):
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

        if not os.path.isfile(fullpath) or settings.DEBUG:
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

            f = open(fullpath, 'w')
            f.write(source)
            f.close()

        return urljoin(self.cache_url, template_name), filename

    def _get_processing_function(self, process_func):
        """
        Retrieves one of the processing functions that can transform our source
        into something else
        
        An example here is using CleverCSS:

            css:
                - static: screen.css
                  process: clevercss
        """
        if not process_func:
            return None

        if self.processing_funcs.has_key(process_func):
            return self.processing_funcs[process_func]
        else:
            raise AttributeError('Could not find a process function matching %s, available ones are: %s' % 
                (process_func, ', '.join(self.processing_funcs.keys()),))

    def __format_css_errors(self, document_raw, errors):
        document = document_raw.split('\n')
        for error in errors:
            yield '%s' % error.getMessage()

    def _fix_css_urls(self, page_instruction, css_source):
        def replacer(url, **kwargs):
            if url.startswith('http') or url.startswith('/'):
                return url

            cache_url = kwargs.get('cache_url')
            relative_path = kwargs.get('relative_path')
            path = os.path.join(relative_path, urllib.url2pathname(url))

            return urljoin(cache_url, urllib.pathname2url(path))

        if not settings.DEBUG:
            cssutils.ser.prefs.useMinified()
        else:
            cssutils.ser.prefs.useDefaults()

        parser = cssutils.CSSParser()
        sheet = parser.parseString(css_source)
        errors = cssutils_handler.get_errors()
        if errors and settings.CRUNCHYFROG_RAISE_CSS_ERRORS:
            formatted_errors = self.__format_css_errors(css_source, errors)
            raise CssFormatError(
                ', '.join(formatted_errors)
            )

        if page_instruction.has_key('static'):
            template_name = page_instruction['static']
        elif page_instruction.has_key('inline'):
            template_name = page_instruction['inline']
        cssutils.replaceUrls(sheet, functools.partial(replacer,
            relative_path=os.path.dirname(template_name),
            cache_url=self.cache_url))
        return sheet.cssText

    def _prepare_file(self, item_name, page_instructions):
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
                self.prepared_instructions[item_name].append(
                    { 'location': instruction['url'] })
            else:
                template_name = context = process_func = None

                if instruction.has_key('process'):
                    process_func = self._get_processing_function(
                        instruction.get('process'))

                item = copy.copy(instruction)

                template_name = instruction.get('static', False) or \
                    instruction.get('inline', False)

                assert template_name, (
                    'You must provide either "static" or "inline" properties '
                    'that point to a file, provided object was %r' % instruction
                )

                if instruction.has_key('inline'):
                    context = self.context
                else:
                    context = None

                source, is_cached = self._get_media_source(template_name, process_func, context)
                if 'css' in item_name and self.make_css_urls_absolute \
                   and not is_cached:
                    source = self._fix_css_urls(instruction, source)

                if instruction.has_key('static'):
                    location, filename = self._copy_to_media(
                        template_name, source)
                    item['location'] = location
                elif instruction.has_key('inline'):
                    item['source'] = source

                if instruction.has_key('include') and not instruction['include']:
                    if instruction.has_key('inline'):
                        raise AttributeError('You have specified inline and '
                            'include: false, these really don\'t make sense '
                            'together')
                    continue

                self.prepared_instructions[item_name].append(item)

    def _prepare_assets(self, page_instructions, assets=None):
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

            self._prepare_assets(pi, ('media/js',))
            self._prepare_assets(pi, ('blog/list/media/js',))

        """
        assert type(assets) == tuple or type(assets) == list

        for yaml in page_instructions.yaml:
            # yaml = app/page/page.yaml
            source, origin = cfloader.find_template_source(yaml)
            del source # we don't need it

            origin = str(origin)
            # /Users/me/Development/app/templates/app/page/page.yaml

            yaml_basedir = os.path.dirname(yaml)
            # app/page
            template_basedir = origin[:origin.find(yaml)] 
            # /Users/me/Development/app/templates

            for asset in assets:
                # directory = /media/js/templates
                if not yaml_basedir in asset:
                    # The user might be specifying the directory relative to the
                    # yaml file itself, so we'll add it for them if they gave us
                    # something like 'media/js/templates'
                    directory = os.path.join(yaml_basedir, asset)
                else:
                    directory = asset

                sourcedirectory = os.path.join(template_basedir, directory)

                if not os.path.isdir(sourcedirectory):
                    # We're going to try and find it somewhere else, it may not
                    # be relative to the YAML file
                    #
                    # This is quite possible if the yaml file is processing a
                    # "ribt:" attribute.
                    try:
                        sourcedirectory = find_directory_from_loader(page_instructions, asset)
                        # We need to reset this, it has the yaml_basedir on it
                        # at this point
                        directory = asset
                    except TemplateDoesNotExist:
                        continue

                if not os.path.isdir(sourcedirectory): continue

                cachedirectory = os.path.join(self.cache_root, directory)

                if os.path.isdir(cachedirectory):
                    if self._assets_are_stale(sourcedirectory, cachedirectory):
                        shutil.rmtree(cachedirectory)
                    else:
                        continue

                shutil.copytree(sourcedirectory, cachedirectory)

    def _assets_are_stale(self, sourcedirectory, cachedirectory):
        """
        Looks through the given directories, determining if they are different
        """
        comparison = filecmp.dircmp(sourcedirectory, cachedirectory, [], [])
        if comparison.left_only or comparison.right_only:
            # We have files in one directory and not the other
            return True
        if comparison.diff_files:
            # Some of the files have changed
            return True

        return False

    def prepare_title(self, page_instructions):
        """
        Prepares the title for the page
        """
        template = Template(str(page_instructions.title))
        self.prepared_instructions['title'] = unicode(template.render(self.context))

    def prepare_body(self, page_instructions):
        """
        Takes the body section and renders it, storing it in prepared_instructions
        """
        template = djangoloader.get_template(str(page_instructions.body))
        self.context['__page_instructions'] = page_instructions
        self.prepared_instructions['body'] = unicode(template.render(self.context))

    def prepare_meta(self, page_instructions):
        """
        Prepares the meta section
        """
        self.prepared_instructions['meta'] = page_instructions.meta

    def prepare_ribt(self, page_instructions):
        ribt_instructions = page_instructions.ribt

        self.prepared_instructions['ribt'] = ribt_instructions

        for ribt_module in ribt_instructions:
            assert 'namespace' in ribt_module, ('You are missing the '
                'namespace attribute for this item')
            assert 'location' in ribt_module, ('You are missing the '
                 'location attribute for this item')
            assert 'require' in ribt_module, ('You are missing the '
                 'require list for this item')

            namespace = ribt_module['namespace']
            location = ribt_module['location']
            require = ribt_module['require']
            ribt_module['needs_registration'] = True

            tests = []
            if ribt.is_instrumented():
                tests = ribt_module.get('tests', tests)

            require.extend(tests)

            """
            We're going to copy all the files that are in this directory to the
            cache.  This is not ideal, as not all the files may be used but the
            alternative is we ask the user specifically which ones they need.
            Since this is within the context of Dojo, that may not make the most
            sense.
            """
            self._prepare_assets(page_instructions, (location,))

    def prepare(self, page_instructions):
        self.page_instructions = page_instructions

        self.prepare_title(page_instructions)
        self.prepare_body(page_instructions)
        self.prepare_js(page_instructions)
        self.prepare_css(page_instructions)
        self.prepare_meta(page_instructions)
        self.prepare_ribt(page_instructions)

        return self.prepared_instructions

class RollupPlan(object):
    """
    These are extra methods that are needed for rolling up files

    A rollup is when you take multiple files and concatenate them into one.
    """
    def _concat_files(self, instructions, fix_css_urls = False):
        source = [] 
        for i in instructions:
            processed = ''
            if i.has_key('source'):
                processed = i['source']
            else:
                processed, is_cached = self._get_media_source(
                    i['static'], self._get_processing_function(i.get('process')))
            if fix_css_urls:
                processed = self._fix_css_urls(i, processed)
            source.append(processed)
        return "\n".join(source)

    def _make_filename(self, files):
        files.sort()
        return hashlib.md5(pickle.dumps(files)).hexdigest()

    def _prepare_rollup(self, attr, rollup, keep, insert_point, **kwargs):
        rollup_instruction = self._rollup_static_files(
            rollup, attr, kwargs.get('minifier', None))
        other_instruction = self.prepared_instructions[attr]
        self.prepared_instructions[attr] = \
            other_instruction[:insert_point] + \
            [rollup_instruction] + \
            other_instruction[insert_point:]

    def _rollup_static_files(self, instructions, extension, minifier=None):
        """
        Creates one file from a list of others.  It also minifies the source
        using the appropriate function
        """
        fix_css_urls = True if 'css' in extension else False

        if not minifier:
            def minifier(arg):
                return arg
        # Figure out a name
        files = [ i['static'] for i in instructions ]

        basename = '%s.%s' % (self._make_filename(files), extension,)
        filename = os.path.join(self.cache_root, basename)
        location = urljoin(self.cache_url, basename)

        if not os.path.isfile(filename) or settings.DEBUG:
            f = open(filename, 'w')
            source = minifier(self._concat_files(instructions, fix_css_urls))
            f.write(source)
            f.close()

        return { 'location': location, }


    def __dojo_register_module_path(self, namespace, basename):
        location = urljoin(self.cache_url, basename)
        js_template= "dojo.registerModulePath('%(namespace)s', '%(location)s');"
        return js_template % {'namespace': namespace, 'location': location}

    def _rollup_ribt(self, ribt_instructions):
        local_modules = []

        for ribt_module in ribt_instructions:
            namespace = ribt_module['namespace']
            location = ribt_module['location']
            require = ribt_module['require']

            # Figure out the path for each requirement based on namespace and
            # location
            for req in require:
                filename = '%s.js' % req.replace('%s.' % namespace, '')
                req_location = os.path.join(location, filename)
                if self.options['unroll_recently_modified']:
                    stat = self._get_media_stat(req_location)
                    if stat and stat.st_mtime > time_started():
                        continue
                source, is_cached = self._get_media_source(req_location)
                # Now we need to add a dojo.registerModulePath to this
                source = '%s\n' % self.__dojo_register_module_path(
                    namespace, location) + source
                # And tell the instructions it no longer needs to worry about
                # the registration of this module
                ribt_module['needs_registration'] = False
                local_modules.append({'name': req, 'static': req_location,
                    'source': source})

        self._local_modules = local_modules

        roll_modules = []

        for mod in self._local_modules:
            self._extract_dojo_requires(roll_modules, mod['name'], mod['static'],
                mod['source'])

        return roll_modules

    def _extract_dojo_requires(self, roll_modules, name, static, source):
        if name in [ i['name'] for i in roll_modules ]:
            return

        req_pattern = re.compile('dojo\.require\((\'|")(?P<mod>[^\'"]+)\\1\)')

        match = req_pattern.findall(source)

        if match == None:
            return
        
        for req_mod in [ i[1] for i in match ]:
            req_mod_path = self._resolve_dojo_module_path(req_mod)
            if not req_mod_path:
                # We couldn't locate it
                raise DojoModuleResolution('Could not resolve %s' % req_mod)
            try:
                req_mod_source, is_cached = self._get_media_source(req_mod_path) 
            except TemplateDoesNotExist as tdne:
                raise TemplateDoesNotExist('Trying to find %s at path %s' % (req_mod, req_mod_path,))

            self._extract_dojo_requires(
                roll_modules, req_mod, req_mod_path, req_mod_source)
        
        # Filter this module out of the prepared instructions, we've now set it
        # to roll in with the other JS
        self._unprepare_ribt_dojo_module(name)

        roll_modules.append({'name': name, 'static': static, 'source': source})

    def _resolve_dojo_module_path(self, mod):
        if not settings.CRUNCHYFROG_DOJO_VIA_INTERNALBUILD:
            # We can only make this work if we use the internal build
            return None

        # It could be in our local_modules
        local = [ i['static'] for i in self._local_modules if i['name'] == mod ]

        if local:
            return local[0]

        mod_parts = mod.split('.')
        mod_path = '%s.js' % os.path.join('ribt', 'media', *mod_parts)

        return mod_path

    def _unprepare_ribt_dojo_module(self, mod):
        for ribt_instruction in self.prepared_instructions['ribt']:
            if mod in ribt_instruction['require']:
                ribt_instruction['require'].remove(mod)
                return
