from time import time

from django.utils.importlib import import_module
from django.conf import settings


class ChirpError(Exception):
    pass

# Used to prevent getting too happy with the autodiscover
_loading = False

# Whether things are instrumented, in other words are we testing?
_instrumented = False

# When we started instrumenting the site, handy for shutting it down after
# a period of time expires
_time_instrumented = None

# List of Chirp modules that need to loaded
# This is to make sure that we don't try and import our Chirp testing modules
# before everything is in place (namely all the urlpatterns)
_chirp_modules = []


def check_instrumentation(meth):
    """
    Decorator to check the main settings and turn on instrumentation if needed
    """
    def check(*args, **kwargs):
        if settings.DEBUG and \
           settings.SKYLARK_CHIRP_INSTRUMENTED and \
           not is_instrumented():
            # The user has indicated that we need to be instrumented for
            # testing
            instrument_site(True)

        return meth(*args, **kwargs)
    return check


def is_instrumented():
    """
    Is the site currently instrumented for testing?
    """
    global _instrumented
    return _instrumented


def page_assembly_testcase_handler(page_instructions, renderer, assembly):
    """
    Used to add the testcase yaml file to the page instructions if we are being
    instrumented (testing)
    """
    assembly.add_page_instructions(
        page_instructions, 'chirp/testrunner/testcase.yaml')


def instrument_site(on):
    """
    Sets a bit within the application that tells every other view that we are
    testing the site using the Chirp test runner.
    """
    from skylark.assembly import BaseAssembly

    global _instrumented, _time_instrumented, _chirp_modules

    if _instrumented and on:
        raise ChirpError('Chirp is already instrumented and ready for testing, '
            'use is_instrumented to detect state')

    _instrumented = on
    _time_instrumented = time()

    if not on:
        # Take our testcase handler out of the loop
        BaseAssembly.unregister_handler(page_assembly_testcase_handler)
        # There is nothing else for us to do here
        return

    BaseAssembly.register_handler(page_assembly_testcase_handler)

    # Now we need to run through all the Chirp modules we found through
    # autodiscover and import them.  We didn't need any of it until we
    # instrumented our site
    for mod in _chirp_modules:
        import_module(mod)


def autodiscover():
    """
    Stolen directory from Django Admin.

    Auto-discover INSTALLED_APPS chirp.py modules and fail silently when
    not present.
    """
    global _loading
    if _loading:
        return
    _loading = True

    import imp
    from django.conf import settings

    global _chirp_modules

    for app in settings.INSTALLED_APPS:
        if app == 'skylark':
            # Skip Django Skylark, these aren't the droids we are looking for
            continue

        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('chirp', app_path)
        except ImportError:
            continue

        _chirp_modules.append("%s.chirp" % app)
    _loading = False


class TestEntryPoint(object):
    def __init__(self, **kwargs):
        self.url = kwargs.get('url', None)
        self.name = kwargs.get('name', None)


class TestRegistry(object):
    _tests = []

    def add(self, url, **kwargs):
        # We don't want to add this if we aren't in DEBUG
        if not settings.DEBUG:
            return

        # We don't want duplicates, that won't help anyone
        if not isinstance(url, (str, unicode)):
            raise ChirpError('You must add URLs to the test registry, not %s' %
                type(url))

        if not url in self:
            self._tests.append(TestEntryPoint(
                url=url, name=kwargs.get('name', None)))

    def clear(self):
        for test in self._tests:
            self._tests.remove(test)

    def __contains__(self, key):
        url = key in [tep.url for tep in self._tests]
        name = key in [tep.name for tep in self._tests]
        return url | name

    def __len__(self):
        return len(self._tests)

    def list(self):
        return self._tests


test_registry = TestRegistry()
