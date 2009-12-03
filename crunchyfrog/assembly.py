import hashlib
import renderer
import yaml
import tidylib
import re

from django import http, template
from django.core.urlresolvers import resolve
from crunchyfrog import HttpResponse, RequestContext
from crunchyfrog.conf import settings
from crunchyfrog.instructions import PageInstructions

tidylib.BASE_OPTIONS = {
    "indent": 1,
    "indent-spaces": 4,
    "quote-marks": 1,
    "tidy-mark": 0,
    "wrap": 0,
    "indent-cdata": 1,
    "force-output": 0,
}

class HtmlTidyErrors(Exception):
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

    def __init__(self, yamlfiles, context):
        if not hasattr(self, 'render_full_page'):
            raise ValueError('You must set render_full_page to True '
                'or False on the subclass of BaseAssembly')

        if not isinstance(context, RequestContext):
            raise ValueError('%r must be of type RequestContext, you provided '
                '%s' % (context, type(context),))

        if not yamlfiles:
            raise ValueError('%r argument must not be empty or None' %
                 (yamlfiles,))

        if not len(yamlfiles):
            raise ValueError('%r must not be zero length' % (yamlfiles,))

        """
        We can get the yamlfiles as a single string or a tuple, but by the time
        we set our instance variable it needs to be normalized to a tuple.

        In other words, this needs to happen:
            'some/file.yaml'   -->  ('some/file.yaml',)
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

    def __create_page_instructions(self):
        """
        Combines all the files and instructions into one object
        """
        page_instructions = PageInstructions(
            render_full_page=self.render_full_page,
            context_instance=self.context
        )

        tried = []

        for file in self.yamlfiles:
            self.__add_page_instructions(page_instructions, file)

        return page_instructions

    def __add_page_instructions(self, page_instructions, file):
        source, origin = template.loader.find_template_source(file)
        assert source, 'The template loader found the template but it is completely empty'

        sourcerendered = template.Template(source).render(self.context)
        assert sourcerendered, 'yamlfile needs to contain something'

        instructions = yaml.load(sourcerendered)

        page_instructions.add(instructions, file)

    def __format_tidy_errors(self, document_raw, errors_raw):
        """
        The errors we get back from the tidy are formatted for output including
        newlines in the string.  Each line is a single error, so we split on the
        line to get a list
        """
        line_pattern = '^line\ (?P<l>\d+)\ column\ (?P<c>\d+)\ \-\ (?P<desc>.*)$'
        line_re = re.compile(line_pattern)

        errors = [ i for i in errors_raw.split('\n') if i ]
        document = document_raw.split('\n')

        for error in errors:
            details = line_re.match(error)
            yield '%s: (%s; line %s)' % (
                details.group('desc'),
                document[int(details.group('l')) - 1],
                details.group('l'),
            )

    def dumps(self):
        instructions = self.__create_page_instructions()

        doctype = instructions.doctype or 'HTML 4.01 Transitional'

        page_renderer = renderer.get(doctype, instructions, self.context,
                                     self.render_full_page)

        content = page_renderer.render()

        if not settings.DEBUG or not self.render_full_page:
            return content

        if not settings.CRUNCHYFROG_ENABLE_TIDY:
            document = content
        else:
            document, errors = tidylib.tidy_document(content)
            if errors and settings.CRUNCHYFROG_RAISE_HTML_ERRORS:
                formatted_errors = self.__format_tidy_errors(content, errors)
                raise HtmlTidyErrors('We tried to tidy up the document and got '
                   'these errors: %s' % 
                   ', '.join(formatted_errors)
                )

        return unicode(document or content)

    def get_http_response(self):
        """
        Returns an HttpResponse object will all the combined goodness
        """
        return HttpResponse(self.dumps())
