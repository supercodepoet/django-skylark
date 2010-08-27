from base import BasePlan


class SeparateEverything(BasePlan):
    def prepare_js(self, page_instructions):
        if not hasattr(page_instructions, 'js'):
            return

        self._prepare_assets(page_instructions, ('media/js/templates',))

        self._prepare_file('js', page_instructions)

    def prepare_css(self, page_instructions):
        if not hasattr(page_instructions, 'css'):
            return

        self._prepare_assets(page_instructions, ('media/img',))

        self._prepare_file('css', page_instructions)
