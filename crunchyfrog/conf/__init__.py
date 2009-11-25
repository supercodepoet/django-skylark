import default as default_settings
from django.conf import settings as django_settings

for name in dir(default_settings):
    if name == name.upper():
        value = getattr(default_settings, name)
        setattr(django_settings, name, value)

settings = django_settings
