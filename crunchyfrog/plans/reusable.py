from base import BasePlan, RollupPlan
from crunchyfrog.utils.jsmin import jsmin

class ReusableFiles(BasePlan, RollupPlan):
    make_css_urls_absolute = True
    cache_prefix = 'rf'

    def __split_static_uses(self, attr, page_instructions):
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

        self._prepare_assets(page_instructions, ('media/js/templates',))

        rollup, keep, insert_point = self.__split_static_uses(
            'js', page_instructions)

        minifier = jsmin

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
