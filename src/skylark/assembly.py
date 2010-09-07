import hashlib
import yaml
import re

from django import http, template
from django.core.urlresolvers import resolve

from skylark import HttpResponse, RequestContext
from skylark.conf import settings
from skylark.instructions import PageInstructions
from skylark import renderer
from skylark import chirp
from skylark.chirp import check_instrumentation

try:
    import tidylib

    tidylib.BASE_OPTIONS = {
        "indent": 1,
        "indent-spaces": 4,
        "quote-marks": 1,
        "tidy-mark": 0,
        "wrap": 0,
        "indent-cdata": 1,
        "force-output": 0,
    }
except OSError:
    """
    We can't use tidy, most likely libtidy is not installed on the system
    """
    settings.SKYLARK_ENABLE_TIDY = False


class HtmlTidyErrors(Exception):
    pass


class HandlerError(Exception):
    pass


class BaseAssembly(object):
    """
    The yaml files we were constructed with, this probably came from a Django
    view
    """
    yamlfiles = None

    """
    The Django template context object we will render everything with
    """
    context = None

    """
    Are we going to render as a full page or a snippet?
    """
    render_full_page = True

    """
    A list of handlers that can be used to alter the Page Assembly before it
    renders content
    """
    _page_assembly_handlers = []

    def __init__(self, yamlfiles, context):
        if not hasattr(self, 'render_full_page'):
            raise ValueError('You must set render_full_page to True '
                'or False on the subclass of BaseAssembly')

        if not isinstance(context, RequestContext):
            raise ValueError('%r must be of type skylark.RequestContext, '
                'you provided %s' % (context, type(context),))

        if not yamlfiles:
            raise ValueError('%r argument must not be empty or None' %
                 (yamlfiles,))

        if not len(yamlfiles):
            raise ValueError('%r must not be zero length' % (yamlfiles,))

        # We can get the yamlfiles as a single string or a tuple, but by the
        # time we set our instance variable it needs to be normalized to a
        # tuple.

        # In other words, this needs to happen:
        #     'some/file.yaml'   -->  ('some/file.yaml',)
        if isinstance(yamlfiles, str):
            yamlfiles = (yamlfiles,)

        self.yamlfiles = yamlfiles

        # It's important for our context to have the media root and url
        # included, if it's not there we are going to add it
        for var in ('MEDIA_ROOT', 'MEDIA_URL'):
            if not hasattr(context, var):
                context[var] = getattr(settings, var)

        self.context = context

        # We keep track of the stack of assemblies that we process, so add this
        # one to the stack
        self.context['skylark_internals']['assembly_stack'].append(self)

    @staticmethod
    def register_handler(handler):
        if not callable(handler):
            raise HandlerError(
                'Handler provided cannot be registered, it is not callable')
        if handler in BaseAssembly._page_assembly_handlers:
            return
        BaseAssembly._page_assembly_handlers.append(handler)

    @staticmethod
    def unregister_handler(handler):
        try:
            BaseAssembly._page_assembly_handlers.remove(handler)
        except ValueError:
            pass

    @staticmethod
    def unregister_all():
        del BaseAssembly._page_assembly_handlers[:]

    def __is_root_assembly(self):
        return True if self == self.__get_root_assembly() else False

    def __get_root_assembly(self):
        astack = self.context['skylark_internals']['assembly_stack']
        return astack[0]

    def __create_page_instructions(self):
        """
        Combines all the files and instructions into one object
        """
        page_instructions = PageInstructions(
            render_full_page=self.render_full_page,
            context_instance=self.context)

        tried = []

        for file in self.yamlfiles:
            self.add_page_instructions(page_instructions, file)

        return page_instructions

    def __convert_tidy_errors(self, errors_raw, **kwargs):
        """
        The errors we get back from the tidy are formatted for output including
        newlines in the string.  Each line is a single error, so we split on
        the line to get a list
        """
        filter = kwargs.get('filter', None)
        pattern = '^line\ (?P<l>\d+)\ column\ (?P<c>\d+)\ \-\ (?P<desc>.*)$'
        line_re = re.compile(pattern)

        errors = []
        for e in errors_raw.split('\n'):
            try:
                line, column, desc = line_re.match(e).groups()
                if [True for i in filter if i in desc]:
                    continue
                errors.append({
                    'line': int(line),
                    'column': int(column),
                    'desc': desc,
                })
            except AttributeError:
                pass

        return errors

    def __format_tidy_errors(self, document_raw, errors):
        document = document_raw.split('\n')

        for error in errors:
            yield '%s: (%s; line %s)' % (
                error['desc'],
                document[error['line'] - 1],
                error['line'],
            )

    def add_page_instructions(self, page_instructions, file):
        source = template.loader.get_template(file)
        assert source, 'The template loader found the template but it is ' + \
            'completely empty'

        sourcerendered = source.render(self.context)
        assert sourcerendered, 'yamlfile needs to contain something'

        instructions = yaml.load(sourcerendered)
        page_instructions.add(instructions, file)

    @check_instrumentation
    def dumps(self):
        self.instructions = self.__create_page_instructions()

        if not self.__is_root_assembly():
            # We are not the root assembly, it's a good bet that we are a
            # SnippetAssembly being rendered within
            root_pa = self.__get_root_assembly()

            # Our media needs to be piped to the root page instructions, we
            # don't want to render media with the SnippetAssembly, the
            # PageAssembly should handle this for us
            self.instructions.pipe_media_to(root_pa.instructions)

        doctype = self.instructions.doctype or 'html'

        page_renderer = renderer.get(doctype, self.instructions, self.context,
            render_full_page=self.render_full_page,
            omit_media=not self.__is_root_assembly())

        for handler in BaseAssembly._page_assembly_handlers:
            handler(self.instructions, page_renderer, self)

        content = page_renderer.render()

        if not settings.DEBUG or not self.render_full_page:
            return content

        if not settings.SKYLARK_ENABLE_TIDY:
            document = content
        else:
            document, errors = tidylib.tidy_document(content)
            # We want to let the proprietary attributes slide, Chirp uses these
            errors = self.__convert_tidy_errors(
                errors, filter=['proprietary attribute'])
            if errors and settings.SKYLARK_RAISE_HTML_ERRORS:
                formatted_errors = self.__format_tidy_errors(content, errors)
                raise HtmlTidyErrors('We tried to tidy up the document and '
                   'got these errors: %s' % ', '.join(formatted_errors))

        return unicode(document or content)

    def get_http_response(self):
        """
        Returns an HttpResponse object will all the combined goodness
        """
        return HttpResponse(self.dumps())
