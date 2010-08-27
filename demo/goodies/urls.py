from django.conf.urls.defaults import *
from skylark.ribt import test_registry

import views

urlpatterns = patterns('',
    (r'^list$', views.list),
)

