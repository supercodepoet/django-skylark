from base import BasePlan, RollupPlan
from skylark.utils.jsmin import jsmin
from skylark import time_started


class ReusableFiles(BasePlan, RollupPlan):
    make_css_urls_absolute = True

    def __split_static_uses(self, attr, page_instructions):
        rollup = []
        keep = []
        insert_point = 0

        for item in getattr(page_instructions, attr):
            if item['sourcefile'] in page_instructions.uses_yaml and \
               'ieversion' not in item and \
               item.get('include', True) and \
               'static' in item:
                rollup.append(item)
                if not insert_point:
                    insert_point = len(keep)
            else:
                keep.append(item)

        return (rollup, keep, insert_point)

    def prepare_js(self, page_instructions):
        if not hasattr(page_instructions, 'js'):
            return

        self._prepare_assets(page_instructions, ('media/js/templates',))

        rollup, keep, insert_point = self.__split_static_uses(
            'js', page_instructions)

        minifier = jsmin if self.options['minify_javascript'] else None

        setattr(page_instructions, 'js', keep)
        self._prepare_file('js', page_instructions)

        self._prepare_rollup('js', rollup, keep, insert_point,
            minifier=minifier)

    def prepare_css(self, page_instructions):
        if not hasattr(page_instructions, 'css'):
            return

        self._prepare_assets(page_instructions, ('media/img',))

        rollup, keep, insert_point = self.__split_static_uses(
            'css', page_instructions)

        setattr(page_instructions, 'css', keep)
        self._prepare_file('css', page_instructions)

        self._prepare_rollup('css', rollup, keep, insert_point)

    def prepare_chirp(self, page_instructions):
        super(ReusableFiles, self).prepare_chirp(page_instructions)

        rollup = self._rollup_chirp(self.prepared_instructions['chirp'])

        # If there is anything left in the chirp instructions, we need to wrap
        # our rolled up chirp content with a dojo.addOnLoad()
        pi_chirp = self.prepared_instructions['chirp']
        if [i['require'] for i in pi_chirp if i['require']]:
            wrap_source = ('dojo.addOnLoad(function() {', '});',)
        else:
            wrap_source = ('', '',)

        minifier = jsmin if self.options['minify_javascript'] else None

        self._prepare_rollup('js', rollup, page_instructions.js,
             len(self.prepared_instructions['js']), minifier=minifier,
             wrap_source=wrap_source)
