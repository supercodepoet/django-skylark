from base import BasePlan

class SeparateEverything(BasePlan):
    cache_prefix = 'se'

    def prepare_js(self, page_instructions):
        if not hasattr(page_instructions, 'js'):
            return

        self.prepare_assets(page_instructions, ('media/js/templates',))

        self.prepare_file('js', page_instructions)

    def prepare_css(self, page_instructions):
        if not hasattr(page_instructions, 'css'):
            return

        self.prepare_assets(page_instructions, ('media/img',))

        self.prepare_file('css', page_instructions)
