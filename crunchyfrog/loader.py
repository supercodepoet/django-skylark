import os
from types import GeneratorType

from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.template import TemplateDoesNotExist
from django.template import loader as djangoloader
from django.conf import settings

template_path_loaders = None


class TemplatePathDoesNotExist(TemplateDoesNotExist):
    pass

def find_template_path(name, dirs=None):
    for loader in djangoloader.template_source_loaders:
        try:
            source, display_name = loader(name, dirs)
            del source
            origin = djangoloader.LoaderOrigin(display_name, loader, name, dirs)
            loader_result = origin.loader.get_template_sources(origin.loadname)
            if type(loader_result) == tuple and len(loader_result) == 2:
                # This is probably a tuple of (source, display_name)
                return loader_result[1]
            elif type(loader_result) == GeneratorType:
                # Means we probably have a list of locations for this template
                # in a generator object, grab the first one and return it
                for path in loader_result:
                    if os.path.isfile(path):
                        return path
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
        template_source_loaders = tuple(loaders)
    for loader in djangoloader.template_source_loaders:
        try:
            source, display_name = loader(name, dirs)
            origin = djangoloader.LoaderOrigin(display_name, loader, name, dirs)
            return (source, origin)
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist(name)