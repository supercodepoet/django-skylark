from base import BasePlan, RollupPlan
from crunchyfrog.utils.jsmin import jsmin
from crunchyfrog import time_started

class FewestFiles(BasePlan, RollupPlan):
    make_css_urls_absolute = True
    cache_prefix = 'ff'

    def __split_static_all(self, attr, page_instructions):
        rollup = [] 
        keep = []
        insert_point = 0

        for item in getattr(page_instructions, attr):
            if not item.has_key('ieversion') and \
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

        self._prepare_assets(page_instructions, ('media/js/templates',))

        rollup, keep, insert_point = self.__split_static_all(
            'js', page_instructions)

        # If there is anything Ribt related, we need to do that here to make it
        # part of our rollup
        super(FewestFiles, self).prepare_ribt(page_instructions)

        rollup.extend(self._rollup_ribt(self.prepared_instructions['ribt']))

        minifier = jsmin if self.options['minify_javascript'] else None

        setattr(page_instructions, 'js', keep)
        self._prepare_file('js', page_instructions)

        self._prepare_rollup('js', rollup, keep, insert_point,
            minifier=minifier)

    def prepare_css(self, page_instructions):
        if not hasattr(page_instructions, 'css'):
            return

        self._prepare_assets(page_instructions, ('media/img',))

        rollup, keep, insert_point = self.__split_static_all(
            'css', page_instructions)

        setattr(page_instructions, 'css', keep)
        self._prepare_file('css', page_instructions)

        self._prepare_rollup('css', rollup, keep, insert_point)

    def prepare_ribt(self, page_instructions):
        # We are going to let the prepare_js handle ribt in this case since we
        # want it to rollup everything JS together.  So there is nothing here to
        # do
        pass

