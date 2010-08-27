from django.template import Template


def add_origin(func):
    """
    We utilize the origin a lot internally for Django Skylark and when a template
    is created with one, we make it available off the Template instance itself.
    This allows us to continue to use the Django loader internals with minimal
    fuss and as much forward compatibility as possible

    Once this patch is applied, and it functions essentially like a decorator,
    we can acces the origin like this::

        >>> template = loader.get_template('some/template.html')
        >>> template.origin
        <django.template.loader.LoaderOrigin object at 0x102e1b710>
        >>> template.origin.name
        u'/Full/Path/to/some/template.html'
    """
    def wrapper(self, template_string,
                origin=None, name='<Unknown Template>'):
        func(self, template_string, origin, name)
        self.origin = origin
    return wrapper

setattr(Template, '__init__', add_origin(Template.__init__))
