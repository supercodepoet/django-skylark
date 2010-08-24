import os
from types import GeneratorType

from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.template import TemplateDoesNotExist
from django.template import loader as djangoloader
from django.conf import settings
from django.template.loader import get_template_from_string

template_path_loaders = None


class TemplatePathDoesNotExist(TemplateDoesNotExist):
    pass

def find_template_path(name, dirs=None):
    for loader in djangoloader.template_source_loaders:
        try:
            source, display_name = loader(name, dirs)
            origin = djangoloader.LoaderOrigin(display_name, loader, name, dirs)
            if hasattr(origin.loader, 'func_name'):
                loader_result = origin.loader(name)
            else:
                loader_result = origin.loader.load_template_source( \
                    origin.loadname)

            return loader_result
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist(name)

def find_template(name, dirs=None):
    # Calculate template_source_loaders the first time the function is executed
    # because putting this logic in the module-level namespace may cause
    # circular import errors. See Django ticket #1292.
    if djangoloader.template_source_loaders is None:
        loaders = []
        for loader_name in settings.TEMPLATE_LOADERS:
            loader = djangoloader.find_template_loader(loader_name)
            if loader is not None:
                loaders.append(loader)
        djangoloader.template_source_loaders = tuple(loaders)
    for loader in djangoloader.template_source_loaders:
        try:
            source, display_name = loader(name, dirs)
            origin = djangoloader.LoaderOrigin(display_name, loader, name, dirs)
            return (source, origin)
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist(name)


def get_template(template_name):
    """
    This is a slight variation of Django's own get_template method,
    returning instead a tuple of the template and the origin for that
    template.

    Returns a compiled Template object for the given template name,
    and the origin of that template, handling template inheritance recursively.
    """
    template, origin = find_template(template_name)
    if not hasattr(template, 'render'):
        # template needs to be compiled
        template = get_template_from_string(template, origin, template_name)
    return (template, origin, )