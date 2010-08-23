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

# To save time, we know of some different method that can be used to get just
# the filename of a template and bypass getting the source, here is how we do
# that

# Try using Django 1.2+ loaders
try:
    from django.template.loaders.filesystem import Loader
    LOADER_REPLACEMENTS = {
        'django.template.loaders.filesystem.loader': \
            'django.template.loaders.filesystem.loader.get_template_sources',
        'django.template.loaders.app_directories.loader': \
            'django.template.loaders.app_directories.loader.get_template_sources',
    }
except ImportError:
# Else fall back to Djanog 1.1- loaders
    LOADER_REPLACEMENTS = {
        'django.template.loaders.filesystem.load_template_source': \
            'django.template.loaders.filesystem.get_template_sources',
        'django.template.loaders.app_directories.load_template_source': \
            'django.template.loaders.app_directories.get_template_sources',
    }


def _make_loader_replacements(loaders):
    """
    Makes replacements for the actual source template loaders with one that
    just returns the path

    Used only by find_template_path
    """
    replacements = []
    for loader in loaders:
        if loader in LOADER_REPLACEMENTS:
            replacements.append(LOADER_REPLACEMENTS[loader])
        else:
            replacements.append(loader)
    return tuple(replacements)


def find_template_path(name, dirs=None):
    """
    Return a path to a template called name

    Django does not include a way to do this easily, their template loader is
    generalized in such a way that it always returns the source of the template
    but not necessarily the origin or display name.

    CF needs the path of the template to perform a lot of it's operations.  The
    source of the file is not always needed, and it takes CPU cycles and disk
    activity to get it most of the time.  So in scenarios where it's not
    required (like stat'ing the template to see when it was last modified) we
    can use find_template_path instead.
    """
    global template_path_loaders
    if template_path_loaders is None:
        loaders = []
        # We need to modify TEMPLATE_LOADERS, both app_directories and
        # filesystem have methods get_template_sources
        template_loaders = _make_loader_replacements(settings.TEMPLATE_LOADERS)
        for path in template_loaders:
            i = path.rfind('.')
            module, attr = path[:i], path[i + 1:]
            try:
                mod = import_module(module)
            except ImportError, e:
                raise ImproperlyConfigured('Error importing template source '
                   'loader %s: "%s"' % (module, e))
            try:
                func = getattr(mod, attr)
            except AttributeError:
                raise ImproperlyConfigured('Module "%s" does not define a '
                   '"%s" callable template source loader' % (module, attr))
            loaders.append(func)
        template_path_loaders = tuple(loaders)
    for loader in template_path_loaders:
        try:
            loader_result = loader(name, dirs)
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
    raise TemplatePathDoesNotExist(name)


def find_template_source(name, dirs=None):
    """
    This is a copy paste job from django.template.loader.

    The reason you find this here is that in DEBUG mode, Django will not return
    the origin, which is imporant to us since we are trying to mirror the
    directory structure and also copy some of the files inside of any media
    directory into the cache as well.

    So, we have to implement our own so that we are always able to
    determining the origin.
    """
    # Calculate template_source_loaders the first time the function is executed
    # because putting this logic in the module-level namespace may cause
    # circular import errors. See Django ticket #1292.
    assert djangoloader.template_source_loaders, (''
        'The template loader has not initialized the '
        'template_source_loader, this is very unusual')

    for loader in djangoloader.template_source_loaders:
        try:
            source, display_name = loader(name, dirs)
            origin = djangoloader.LoaderOrigin(
                display_name, loader, name, dirs)
            return (source, origin)
        except TemplateDoesNotExist:
            pass

    raise TemplateDoesNotExist(name)
