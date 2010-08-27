from django.core.urlresolvers import reverse

from skylark.ribt import test_registry

test_registry.add('/url', name="Test entry point")
