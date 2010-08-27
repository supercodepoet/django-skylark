from django.core.urlresolvers import reverse

from skylark.ribt import test_registry

import views

test_registry.add(reverse(views.list), name="List my goodies")
