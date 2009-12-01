import os
import pickle
import hashlib
import cssutils
import functools
import urllib

from urlparse import urljoin
from base import BasePlan
from django import template
from crunchyfrog.utils.jsmin import jsmin
from crunchyfrog.conf import settings

cssutils.ser.prefs.useMinified()

class ReusableFiles(BasePlan):
    cache_prefix = 'rf'

    def _fix_css_urls(self, page_instruction, css_source):
        def replacer(url, **kwargs):
            if url.startswith('http') or url.startswith('/'):
                return url

            cache_url = kwargs.get('cache_url')
            relative_path = kwargs.get('relative_path')
            path = os.path.join(relative_path, urllib.url2pathname(url))

            return urljoin(cache_url, urllib.pathname2url(path))

        parser = cssutils.CSSParser()
        sheet = parser.parseString(css_source)
        cssutils.replaceUrls(sheet, functools.partial(replacer,
            relative_path=os.path.dirname(page_instruction['static']),
            cache_url=self.cache_url))
        return sheet.cssText

    def __concat_files(self, instructions, fix_css_urls = False):
        source = [] 
        for i in instructions:
            processed = self.get_media_source(
                i['static'], self._get_processing_function(i.get('process')))
            if fix_css_urls:
                processed = self._fix_css_urls(i, processed)
            source.append(processed)
        return "\n".join(source)

    def __make_filename(self, files):
        files.sort()
        return hashlib.md5(pickle.dumps(files)).hexdigest()

    def __rollup_static_files(self, instructions, extension, minifier = None):
        fix_css_urls = True if 'css' in extension else False

        if not minifier:
            def minifier(arg):
                return arg
        """
        Creates one file from a list of others.  It also minifies the source
        using the appropriate function
        """
        # Figure out a name
        files = [ i['static'] for i in instructions ]

        basename = '%s.%s' % (self.__make_filename(files), extension,)
        filename = os.path.join(self.cache_root, basename)
        location = urljoin(self.cache_url, basename)

        if not os.path.isfile(filename) or settings.DEBUG:
            f = open(filename, 'w')
            source = minifier(self.__concat_files(instructions, fix_css_urls))
            f.write(source)
            f.close()

        return { 'location': location, }

    def _split_static_uses(self, attr, page_instructions):
        rollup = [] 
        keep = []
        insert_point = 0

        for item in getattr(page_instructions, attr):
            if item['sourcefile'] in page_instructions.uses_yaml and \
               not item.has_key('ieversion') and \
               item.get('include', True) and \
               item.has_key('static'):
                rollup.append(item)
                if not insert_point:
                    insert_point = len(keep)
            else:
                keep.append(item)

        return (rollup, keep, insert_point)

    def prepare_js(self, page_instructions):
        if not hasattr(page_instructions, 'js'):
            return

        self.prepare_assets(page_instructions, ('media/js/templates',))

        rollup, keep, insert_point = self._split_static_uses(
            'js', page_instructions)

        setattr(page_instructions, 'js', keep)
        self.prepare_file('js', page_instructions)

        rollup_instruction = self.__rollup_static_files(rollup, 'js', jsmin)
        other_instruction = self.prepared_instructions['js']
        self.prepared_instructions['js'] = \
            other_instruction[:insert_point] + \
            [rollup_instruction] + \
            other_instruction[insert_point:]

    def prepare_css(self, page_instructions):
        if not hasattr(page_instructions, 'css'):
            return

        self.prepare_assets(page_instructions, ('media/img',))

        rollup, keep, insert_point = self._split_static_uses(
            'css', page_instructions)

        setattr(page_instructions, 'css', keep)
        self.prepare_file('css', page_instructions)
        rollup_instruction = self.__rollup_static_files(rollup, 'css')

        other_instruction = self.prepared_instructions['css']
        self.prepared_instructions['css'] = \
            other_instruction[:insert_point] + \
            [rollup_instruction] + \
            other_instruction[insert_point:]
