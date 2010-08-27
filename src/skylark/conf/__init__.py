import default as default_settings
from django.conf import settings as django_settings
from django.utils.functional import LazyObject


class SkylarkSettings(LazyObject):
    def _setup(self):
        for name in dir(default_settings):
            if name == name.upper() and \
               not hasattr(django_settings, name):
                value = getattr(default_settings, name)
                setattr(django_settings, name, value)

        self._wrapped = django_settings

settings = SkylarkSettings()
